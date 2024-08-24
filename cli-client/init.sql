create table if not exists server (
	id integer primary key autoincrement,

	url text,
	trusted bool
);

create table if not exists address (
	id integer primary key autoincrement,

	-- hosting details (universal resource location and access credentials)
	name text,
	server integer,
	auth text,  -- null if the address is not owned

	keys text, -- versioned json blob

	foreign key (server) references server (id)
);

create table if not exists room (
	id integer primary key autoincrement,

	name text,
	server integer,
	auth text,

	keys text,

	-- sync to prevent race conditions
	last_hash text default '',

	foreign key (server) references server (id)
);

create table if not exists broadcast (
	id integer primary key autoincrement,

	name text,
	server integer,
	auth text,

	keys text,

	foreign key (server) references server (id)
);

-- encrypted message
create table if not exists message (
	id integer primary key autoincrement,

	-- messages also have universal resource ids (<message id>@<address id>@<server url>)
	address integer,
	name text, -- id to remove the message

	data text,

	remote_copy boolean, -- if true, can delete locally to download again

	foreign key (address) references address (id)
);

-- TODO:
-- parse messages with non-text content (in messaging.py) and store their information in special object tables

-- the following tables represent objects stored within messages, and deleted with them
-- these objects are standalone (not related to the rest of the database)

-- room invite
create table if not exists room_info (
	id integer primary key autoincrement,

	message integer,

	-- room details
	-- not linked with the rest of the database
	url text,
	auth text,
	keys text,

	foreign key (message) references message (id) on delete cascade
);

-- address contact
create table if not exists address_info (
	id integer primary key autoincrement,

	message integer,

	url text,
	--auth text, -- the auth is only needed when giving away the entire address
	keys text,

	foreign key (message) references message (id) on delete cascade

);

-- broadcast access
create table if not exists broadcast_info (
	id integer primary key autoincrement,

	message integer,

	url text,
	keys text,

	foreign key (message) references message (id) on delete cascade
);
