import os

bind = "0.0.0.0:" + os.environ.get("PORT", "8000")
workers = 1    # one worker keeps the login lockout counter in one place
threads = 4    # still handles several visitors at once
timeout = 60
