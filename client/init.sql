create table if not exists server (
	id integer primary key autoincrement,
	url text unique

	-- vanity
	--label text,
	--enabled bool default true
);

--create trigger if not exists server_label
--after insert on server
--begin
--	update server
--	set label = inserted.url
--	where id = inserted.id;
--end;


create table if not exists store (
	id integer primary key autoincrement,

	name text,
	server integer,
	auth text,

	aes_key text,

	-- vanity
	--label text,
	--enabled bool default true,
	
	foreign key (server) references server (id)
);

--create trigger if not exists store_label
--after insert on store
--begin
--	update store
--	set label = concat(name, "@",
--		(select url from server
--		where server.id = store.server))
--	where id = inserted.id;
--end;



create table if not exists address (
	id integer primary key autoincrement,

	name text,
	server integer,
	auth text,

	-- vanity
	--label text,
	--enabled bool default true,

	key_name text,
	
	foreign key (server) references server (id)
);

--create trigger if not exists address_label
--after insert on address
--begin
--	update address
--	set label = concat(name, "@",
--		(select url from server
--		where server.id = address.server))
--	where id = inserted.id;
--end;


-- set "server" field to null on stores and message addresses
create trigger if not exists server_delete 
before delete on server
begin
	update store
	set server = null
	where server = deleted.id;

	update message_address
	set server = null
	where server = deleted.id;
end;


create table if not exists message (
	id integer primary key autoincrement,

	address integer,
	data text,
	decoded integer default null,

	-- removed from the server ?
	--removed bool, -- boolean (TRUE or FALSE)

	foreign key (address) references address (id),
	foreign key (decoded) references invite (id)
);

create table if not exists invite (
	id integer primary key autoincrement,
	message integer,

	name text,
	server text,

	--store integer,

	-- reading an invite is enough to accept it ?
	--accepted bool default false,

	foreign key (message) references message (id)
	--foreign key (store) references store (id)
);

