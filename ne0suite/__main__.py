# lets `python -m ne0suite` work without installing the entry point first
from ne0suite.cli import main

if __name__ == "__main__":
    main()
