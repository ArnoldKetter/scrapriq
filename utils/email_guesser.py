# scrapriq/utils/email_guesser.py

def generate_email_guesses(first_name: str, last_name: str, domain: str) -> list[str]:
    """
    Generates a list of common email format guesses based on first name, last name, and domain.
    """
    first_name_lower = first_name.lower()
    last_name_lower = last_name.lower()
    
    guesses = []

    # Common patterns [cite: 28, 58, 113, 221]
    guesses.append(f"{first_name_lower}.{last_name_lower}@{domain}") # first.last@domain [cite: 28, 113, 222]
    guesses.append(f"{first_name_lower}@{domain}")                   # first@domain [cite: 224]
    guesses.append(f"{last_name_lower}@{domain}")                    # last@domain
    guesses.append(f"{first_name_lower[0]}{last_name_lower}@{domain}") # f.last@domain [cite: 223]
    guesses.append(f"{first_name_lower}{last_name_lower}@{domain}")  # firstlast@domain
    guesses.append(f"{first_name_lower[0]}.{last_name_lower}@{domain}") # f.last@domain [cite: 223]

    # Less common but possible patterns
    if len(first_name_lower) > 1:
        guesses.append(f"{first_name_lower}{last_name_lower[0]}@{domain}") # firstl@domain
        guesses.append(f"{first_name_lower}.{last_name_lower[0]}@{domain}") # first.l@domain
    
    # Remove duplicates while preserving order
    return list(dict.fromkeys(guesses))

# Example Usage:
if __name__ == "__main__":
    test_first = "John"
    test_last = "Doe"
    test_domain = "example.com"
    emails = generate_email_guesses(test_first, test_last, test_domain)
    print(f"Guessed emails for {test_first} {test_last} at {test_domain}:")
    for email in emails:
        print(email)

    test_first_short = "Li"
    test_last_short = "Wang"
    test_domain_short = "company.io"
    emails_short = generate_email_guesses(test_first_short, test_last_short, test_domain_short)
    print(f"\nGuessed emails for {test_first_short} {test_last_short} at {test_domain_short}:")
    for email in emails_short:
        print(email)