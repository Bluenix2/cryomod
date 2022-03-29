CREATE TABLE cases(
    id INT NOT NULL PRIMARY KEY GENERATED AS IDENTITY ALWAYS,
    guild_id bigint NOT NULL,
    case_id INT NOT NULL,
    type smallint NOT NULL,

    actor_id bigint NOT NULL,
    user_id bigint NOT NULL,

    notified boolean NOT NULL DEFAULT FALSE,
    created_at timestamp NOT NULL WITH TIME ZONE DEFAULT (NOW() AT TIME ZONE 'utc'),
    expires_at timestamp WITH TIME ZONE, -- This is purposefully nullable

    UNIQUE INDEX guild_cases_idx (guild_id, case_id),
    INDEX actor_cases_idx (guild_id, actor_id) INCLUDE (case_id),
    INDEX user_cases_idx (guild_id, user_id) INCLUDE (case_id),
    INDEX expiring_cases_idx (guild_id, expires_at) WHERE expires_at IS NOT NULL,
);
