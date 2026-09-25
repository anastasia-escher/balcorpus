# Only for checking the PHP backend locally; the real server is Plesk.
# PHP 8.1 is the oldest version the code has to run on.
FROM php:8.1-apache

# pdo_mysql talks to MariaDB, zip builds the .xlsx export. mbstring is
# already part of the image.
RUN apt-get update && \
    apt-get install -y --no-install-recommends libzip-dev && \
    docker-php-ext-install pdo_mysql zip && \
    apt-get clean && rm -rf /var/lib/apt/lists/*

# The production settings, as on the server: warnings go to the log, not into
# the JSON the site reads.
RUN cp "$PHP_INI_DIR/php.ini-production" "$PHP_INI_DIR/php.ini"
