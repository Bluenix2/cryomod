CREATE TABLE reminders(
    id int PRIMARY KEY GENERATED AS IDENTITY ALWAYS,
    channel_id bigint NOT NULL,
    author_id bigint NOT NULL,

    guild_id bigint,
    delivered bool NOT NULL DEFAULT false,

    created_at timestamp NOT NULL WITH TIME ZONE DEFAULT (NOW() AT TIME ZONE 'utc'),
    expires_at timestamp NOT NULL WITH TIME ZONE,

    INDEX active_reminders_idx (guild_id, author_id) WHERE delivered = false
        INCLUDE (expires_at, channel_id),

    INDEX expiring_reminders_idx (expires_at) WHERE delivered = false ORDER BY expires_at ASC
);
