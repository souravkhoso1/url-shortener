# shortener/utils.py


def get_identicon_url(username):
    """
    Generate local identicon URL for a given username.

    Args:
        username: User's username

    Returns:
        Local identicon URL string
    """
    return f"/identicon/{username}.png"
