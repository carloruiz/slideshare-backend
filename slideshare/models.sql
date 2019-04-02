CREATE EXTENSION IF NOT EXISTS citext;

CREATE TABLE "user" (
    id SERIAL PRIMARY KEY,
    username VARCHAR(15) UNIQUE,
    email VARCHAR(30) UNIQUE,
    password VARCHAR,
);

CREATE TABLE "user"_meta (
    id SERIAL PRIMARY KEY,
    userid INTEGER REFERENCES "user"(id) ON DELETE SET NULL UNIQUE,
    firstname VARCHAR(30),
    lastname VARCHAR(30),
    joined_on timestamp without time zone,
    last_login timestamp without time zone,
    user_type VARCHAR(15)
);

CREATE TABLE slide_id (
    id SERIAL PRIMARY KEY
);

CREATE TABLE slide (
    id INTEGER PRIMARY KEY REFERENCES slide_id(id) ON DELETE CASCADE,
    title citext,
    url VARCHAR UNIQUE,
	thumbnail VARCHAR UNIQUE NOT NULL,
	pdf VARCHAR UNIQUE NOT NULL,
    userid INTEGER REFERENCES "user"(id) ON DELETE CASCADE,
    username VARCHAR(15) REFERENCES "user"(username) ON DELETE CASCADE ON UPDATE CASCADE,
    size VARCHAR(20),
    description VARCHAR,
    created_on timestamp without time zone,
    last_mod timestamp without time zone,
);


CREATE TABLE tag (
    id SERIAL PRIMARY KEY,
    tag citext UNIQUE
);

CREATE TABLE slide_tag (
    slide INTEGER REFERENCES slide_id(id) ON DELETE CASCADE,
    tag INTEGER REFERENCES tag(id) ON DELETE CASCADE,
    CONSTRAINT slide_tag_pk PRIMARY KEY (slide, tag)
);


CREATE TABLE institution (
    id SERIAL PRIMARY KEY,
    name VARCHAR,
    state VARCHAR(30),
    CONSTRAINT unique_name_state UNIQUE (name, state)
);

CREATE TABLE affiliation (
    id SERIAL PRIMARY KEY,
    "user" INTEGER REFERENCES "user"(id) ON DELETE CASCADE,
    institution INTEGER REFERENCES institution(id) ON DELETE CASCADE,
    CONSTRAINT unique_user_institution UNIQUE (user, institution)
);
