create table if not exists server (
	id integer primary key autoincrement,

	url text,
	trusted bool
);

create table if not exists address (
	id integer primary key autoincrement,

	name text,
	server integer,

	-- the server is owned if there is a key for it and an auth password
	-- foreign addresses only have primary keys
	auth text,
	key_name text,

	foreign key (server) references server (id)
);

create table if not exists room (
	id integer primary key autoincrement,

	name text,
	server integer,

	auth text,
	-- TODO: allow more key types
	-- currently: AES everywhere
	sym_key text,
	--data_file text,

	-- sync to prevent race conditions
	last_hash text default '',

	foreign key (server) references server (id)
);

-- encrypted message
create table if not exists message (
	id integer primary key autoincrement,

	address integer,
	name text, -- id to remove the message
	data text,
	remote_copy boolean,

	foreign key (address) references address (id)
);

-- decrypted invite messages
create table if not exists invite (
	id integer primary key autoincrement,

	-- an invite is contained in a message
	message integer,

	room_name text,
	--room_server integer,
	room_server text,
	room_auth text,
	room_key text,

	foreign key (message) references message (id) on delete cascade
	--foreign key (room_server) references server (id)
);

create table if not exists broadcast (
	id integer primary key autoincrement,

	name text,
	server integer,
	auth text,
	auth_key text, --asymetric signing key
	access_key text, --symetric key

	foreign key (server) references server (id)
);

