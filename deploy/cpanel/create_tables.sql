-- Tag-BD bot tables, for the SQL_DATABASE_URL database. Run in phpMyAdmin.
-- Only needed if this database does not already have them.

CREATE TABLE IF NOT EXISTS user_info (
    chat_id BIGINT PRIMARY KEY,
    username VARCHAR(255),
    admin_id BIGINT
);

CREATE TABLE IF NOT EXISTS bd_replies (
    id BIGINT AUTO_INCREMENT PRIMARY KEY,
    first_message TEXT,
    original_message_id BIGINT,
    tagged_admin_id BIGINT,
    reply_message_id BIGINT,
    chat_id BIGINT,
    replier_username VARCHAR(255),
    reply_text TEXT,
    created_at TIMESTAMP,
    updated_at TIMESTAMP NULL ON UPDATE CURRENT_TIMESTAMP
);
