# hibp-cli
Utilizes haveibeenpwned.com's API for command line search results

* Pulls pastes and domains from a list of emails/usernames or single search term
* Uses the Adobe password dump (not included) and searches haveibeenpwned.com from results with the same base 64 password as the input

_See Naked Security's [post](https://nakedsecurity.sophos.com/2013/11/04/anatomy-of-a-password-disaster-adobes-giant-sized-cryptographic-blunder/) on the password anatomy_


# Prerequisites
* Python 2.7
* grep (cygwin on windows)


# How to
Search term from one or many strings

```python hibp-cli.py -s example@email.com```

Search term from file:

```python hibp-cli.py -f emails.txt```
<br /><br /><br />
Search a list of emails from Adobe dump and return haveibeenpwned's results from matching base64 passwords

```python hibp-cli.py -a -f emails.txt```

Results will look like this:

```
example@email.com:hackedwebsite.com
coolusername:pastebin.com/paste
```
