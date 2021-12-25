CREATE TABLE IF NOT EXISTS guilds (
	GuildID integer PRIMARY KEY,
	Prefix text DEFAULT "?"
);

CREATE TABLE IF NOT EXISTS bibliotecarios (
    UserID integer,
    nome text,
    guildID integer
);

CREATE TABLE IF NOT EXISTS links (
    LinkID text PRIMARY KEY,
    LinkURL text
);


CREATE TABLE IF NOT EXISTS threat (
    UserID integer,
    userName text,
    Positivos integer,
    Potencial integer,
    LinkScan text,
    ArquivoLink text
);

CREATE TABLE IF NOT EXISTS channels (
    GuildID integer,
    name text,
    channelID integer
);

CREATE TABLE IF NOT EXISTS upload (
    messageID integer PRIMARY KEY,
    userID integer,
    userName text,
    idiom text,
    hashtag text,
    title text,
    LinkF text,
    scanL text,
    PdfPath text,
    status text
);
CREATE TABLE IF NOT EXISTS mutes (
    UserID integer,
    GuildID integer,
    RoleIDs text,
    EndTime text,
    Rolemute integer
);

CREATE TABLE IF NOT EXISTS expg (
    UniqueID text PRIMARY KEY,
	XP integer DEFAULT 0,
	Level integer DEFAULT 0,
	XPLock text DEFAULT CURRENT_TIMESTAMP
);
CREATE TABLE IF NOT EXISTS exp (
	UserID integer PRIMARY KEY,
	XP integer DEFAULT 0,
	Level integer DEFAULT 0,
	XPLock text DEFAULT CURRENT_TIMESTAMP
);

