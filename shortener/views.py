# shortener/views.py
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.models import User
from django.contrib import messages
from django.http import HttpResponse
from .models import ShortenedURL, PasswordResetToken, UserProfile
from .forms import URLForm, UserRegisterForm, UserLoginForm, PasswordResetRequestForm, PasswordResetConfirmForm, UserUpdateForm, ProfilePhotoUpdateForm
from .email_utils import send_password_reset_email
from .utils import get_identicon_url
from .identicon_utils import generate_identicon_response


def home(request):
    # Get total count of all shortened URLs
    total_urls = ShortenedURL.objects.count()

    if request.method == 'POST':
        # Only allow logged-in users to shorten URLs
        if not request.user.is_authenticated:
            messages.error(request, 'Please login or register to shorten URLs.')
            return redirect('shortener:login')

        form = URLForm(request.POST)
        if form.is_valid():
            original_url = form.cleaned_data['url']
            custom_code = form.cleaned_data.get('custom_code')

            # If custom code provided, use it regardless of existing URLs
            if custom_code:
                short_code = custom_code
                shortened = ShortenedURL.objects.create(
                    original_url=original_url,
                    short_code=short_code,
                    user=request.user
                )
            else:
                # Check if URL already exists for this user
                existing = ShortenedURL.objects.filter(
                    original_url=original_url,
                    user=request.user
                ).first()

                if existing:
                    shortened = existing
                else:
                    short_code = ShortenedURL.generate_short_code()
                    shortened = ShortenedURL.objects.create(
                        original_url=original_url,
                        short_code=short_code,
                        user=request.user
                    )

            short_url = request.build_absolute_uri(f'/{shortened.short_code}')

            return render(request, 'shortener/home.html', {
                'form': URLForm(),
                'short_url': short_url,
                'shortened': shortened,
                'total_urls': total_urls
            })
    else:
        form = URLForm()

    return render(request, 'shortener/home.html', {
        'form': form,
        'total_urls': total_urls
    })


@login_required
def my_urls(request):
    urls = ShortenedURL.objects.filter(user=request.user).order_by('-created_at')
    return render(request, 'shortener/my_urls.html', {'urls': urls})


def redirect_url(request, short_code):
    url_obj = get_object_or_404(ShortenedURL, short_code=short_code)
    url_obj.clicks += 1
    url_obj.save()
    return redirect(url_obj.original_url)


def stats(request, short_code):
    url_obj = get_object_or_404(ShortenedURL, short_code=short_code)

    # Check if user owns this URL
    is_owner = request.user.is_authenticated and url_obj.user == request.user

    return render(request, 'shortener/stats.html', {
        'url_obj': url_obj,
        'is_owner': is_owner
    })


def register(request):
    if request.user.is_authenticated:
        return redirect('shortener:home')

    if request.method == 'POST':
        form = UserRegisterForm(request.POST)
        if form.is_valid():
            user = form.save()
            username = form.cleaned_data.get('username')
            messages.success(request, f'Account created for {username}! You can now log in.')
            return redirect('shortener:login')
    else:
        form = UserRegisterForm()

    return render(request, 'shortener/register.html', {'form': form})


def user_login(request):
    if request.user.is_authenticated:
        return redirect('shortener:home')

    if request.method == 'POST':
        form = UserLoginForm(data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(username=username, password=password)
            if user is not None:
                login(request, user)
                messages.success(request, f'Welcome back, {username}!')
                next_page = request.GET.get('next', 'shortener:home')
                return redirect(next_page)
    else:
        form = UserLoginForm()

    return render(request, 'shortener/login.html', {'form': form})


def user_logout(request):
    logout(request)
    messages.info(request, 'You have been logged out.')
    return redirect('shortener:home')


def password_reset_request(request):
    """Handle password reset request - user enters username"""
    if request.user.is_authenticated:
        return redirect('shortener:home')

    if request.method == 'POST':
        form = PasswordResetRequestForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data['username']
            user = User.objects.get(username=username)

            # Create password reset token
            reset_token = PasswordResetToken.create_for_user(user, expiry_hours=24)

            # Build reset link
            reset_link = request.build_absolute_uri(
                f'/password-reset/confirm/{reset_token.token}/'
            )

            # Send email using MailerSend
            email_sent = send_password_reset_email(
                user_email=user.email,
                username=user.username,
                reset_link=reset_link
            )

            if email_sent:
                messages.success(
                    request,
                    f'Password reset link has been sent to the email address associated with {username}.'
                )
            else:
                messages.warning(
                    request,
                    'There was an issue sending the email. Please contact support or try again later.'
                )

            return redirect('shortener:login')
    else:
        form = PasswordResetRequestForm()

    return render(request, 'shortener/password_reset_request.html', {'form': form})


def password_reset_confirm(request, token):
    """Handle password reset confirmation - user enters new password"""
    # Get the reset token
    reset_token = get_object_or_404(PasswordResetToken, token=token)

    # Check if token is valid
    if not reset_token.is_valid():
        messages.error(request, 'This password reset link is invalid or has expired.')
        return redirect('shortener:password_reset_request')

    if request.method == 'POST':
        form = PasswordResetConfirmForm(request.POST)
        if form.is_valid():
            # Set new password
            new_password = form.cleaned_data['password1']
            user = reset_token.user
            user.set_password(new_password)
            user.save()

            # Mark token as used
            reset_token.mark_as_used()

            messages.success(
                request,
                'Your password has been reset successfully. You can now log in with your new password.'
            )
            return redirect('shortener:login')
    else:
        form = PasswordResetConfirmForm()

    return render(request, 'shortener/password_reset_confirm.html', {
        'form': form,
        'token': token
    })


@login_required
def profile(request):
    """Display user profile"""
    # Ensure user has a profile (should be created automatically, but just in case)
    profile, created = UserProfile.objects.get_or_create(user=request.user)

    # Get Identicon URL
    gravatar_url = get_identicon_url(request.user.username)

    # Get user's stats
    total_urls = ShortenedURL.objects.filter(user=request.user).count()
    total_clicks = sum(url.clicks for url in ShortenedURL.objects.filter(user=request.user))

    context = {
        'profile': profile,
        'gravatar_url': gravatar_url,
        'total_urls': total_urls,
        'total_clicks': total_clicks,
    }

    return render(request, 'shortener/profile.html', context)


@login_required
def edit_profile(request):
    """Edit user profile information and photo"""
    # Ensure user has a profile
    profile, created = UserProfile.objects.get_or_create(user=request.user)

    if request.method == 'POST':
        user_form = UserUpdateForm(request.POST, instance=request.user)
        photo_form = ProfilePhotoUpdateForm(request.POST, request.FILES, instance=profile)

        if user_form.is_valid() and photo_form.is_valid():
            user_form.save()
            photo_form.save()
            messages.success(request, 'Your profile has been updated successfully!')
            return redirect('shortener:profile')
    else:
        user_form = UserUpdateForm(instance=request.user)
        photo_form = ProfilePhotoUpdateForm(instance=request.user.profile)

    gravatar_url = get_identicon_url(request.user.username)

    context = {
        'user_form': user_form,
        'photo_form': photo_form,
        'gravatar_url': gravatar_url,
        'profile': profile,
    }

    return render(request, 'shortener/edit_profile.html', context)


def serve_identicon(request, username):
    """
    Generate and serve an identicon image for a given username.
    """
    image_buffer = generate_identicon_response(username)
    return HttpResponse(image_buffer.getvalue(), content_type='image/png')