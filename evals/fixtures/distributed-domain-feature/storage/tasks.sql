-- task lease state lives here
create table tasks (id text primary key, lease_until text);
