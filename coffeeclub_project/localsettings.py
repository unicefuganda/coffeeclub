COUNTRY_CALLING_CODE = '256'
BACKEND_PREFIXES = [('70', 'warid'), ('75', 'zain'), ('71', 'utl'), ('', 'dmark')]

# for postgresql:
DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.postgresql_psycopg2",
        "NAME": "coffeeclub",
        "USER": "postgres",
	"PASSWORD": "postgres",
    }
}

