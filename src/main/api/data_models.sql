create table solves (
    id bigint generated always as identity primary key,
    solve_time_ms bigint not null,
    moves integer not null,
    created_at timestamptz default now(),
    nickname text
);

create table solves_dev (
    id bigint generated always as identity primary key,
    solve_time_ms bigint not null,
    moves integer not null,
    created_at timestamptz default now(),
    nickname text
);