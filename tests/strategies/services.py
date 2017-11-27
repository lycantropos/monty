import string

from hypothesis import strategies

from .common import ascii_alphanumeric

dockerhub_logins = strategies.just('lycantropos')
github_logins = strategies.just('lycantropos')

invalid_dockerhub_logins_alphabet = strategies.characters(
        blacklist_characters=string.ascii_letters)
invalid_dockerhub_logins = (
    strategies.text(alphabet=invalid_dockerhub_logins_alphabet)
    | strategies.text(max_size=3)
    | strategies.text(min_size=31))

invalid_github_logins_alphabet = strategies.characters(
        blacklist_characters=ascii_alphanumeric)
invalid_github_logins = (
    strategies.text(alphabet=invalid_github_logins_alphabet)
    | strategies.text(min_size=40))