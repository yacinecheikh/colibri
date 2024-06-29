create table server if not exists (
	id primary key,
	url
)

create table symetric_key if not exists (
	key
)

create table asymetric_key if not exists (
	public_key,
	private_key
)


create table message_address if not exists (
	address,
	server integer,
	private_key,
	public_key,

	foreign key (server) references server (rowid) on delete cascade
)


