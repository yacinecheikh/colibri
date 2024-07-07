-- TODO: add more fields (server.trusted,...)
create table if not exists server (
	id integer primary key autoincrement,

	url text
);

create table if not exists address (
	id integer primary key autoincrement,

	name text,
	server integer,

	-- the server is owned if there is a key for it and an auth password
	-- foreign addresses only have primary keys
	auth text,
	-- name@server may not be a valid folder name
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


	-- room@server may not be a valid folder name
	data_file text,
	--data_dir text,

	foreign key (server) references server (id)
);

-- encrypted message
create table if not exists message (
	id integer primary key autoincrement,

	address integer,
	name text, -- id to remove the message
	data text,

	foreign key (address) references address (id)
);

-- decrypted invite messages
create table if not exists invite (
	id integer primary key autoincrement,

	message integer,

	room_name text,
	room_server integer,
	sym_key text,

	foreign key (message) references message (id)
	foreign key (room_server) references server (id)
);

