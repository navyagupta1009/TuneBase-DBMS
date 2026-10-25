
CREATE DATABASE IF NOT EXISTS TuneBase;
USE TuneBase;


CREATE TABLE Users (
    user_id INT AUTO_INCREMENT PRIMARY KEY,
    username VARCHAR(50) NOT NULL UNIQUE,
    email VARCHAR(100) NOT NULL UNIQUE,
    password_hash VARCHAR(255) NOT NULL,
    join_date DATE NOT NULL DEFAULT (CURRENT_DATE)
);


CREATE TABLE Artists (
    artist_id INT AUTO_INCREMENT PRIMARY KEY,
    artist_name VARCHAR(100) NOT NULL,
    country VARCHAR(50)
);


CREATE TABLE Albums (
    album_id INT AUTO_INCREMENT PRIMARY KEY,
    album_title VARCHAR(150) NOT NULL,
    release_date DATE,
    artist_id INT NOT NULL,
    FOREIGN KEY (artist_id)
        REFERENCES Artists(artist_id)
);


CREATE TABLE Songs (
    song_id INT AUTO_INCREMENT PRIMARY KEY,
    song_title VARCHAR(150) NOT NULL,
    duration_seconds INT NOT NULL,
    genre VARCHAR(50),
    album_id INT NOT NULL,
    CHECK (duration_seconds > 0),
    FOREIGN KEY (album_id)
        REFERENCES Albums(album_id)
);


CREATE TABLE Playlists (
    playlist_id INT AUTO_INCREMENT PRIMARY KEY,
    playlist_name VARCHAR(100) NOT NULL,
    user_id INT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id)
        REFERENCES Users(user_id)
        ON DELETE CASCADE
);


CREATE TABLE Playlist_Songs (
    playlist_id INT NOT NULL,
    song_id INT NOT NULL,
    added_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (playlist_id, song_id),
    FOREIGN KEY (playlist_id)
        REFERENCES Playlists(playlist_id)
        ON DELETE CASCADE,
    FOREIGN KEY (song_id)
        REFERENCES Songs(song_id)
        ON DELETE CASCADE
);


CREATE TABLE Likes (
    user_id INT NOT NULL,
    song_id INT NOT NULL,
    liked_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (user_id, song_id),
    FOREIGN KEY (user_id)
        REFERENCES Users(user_id)
        ON DELETE CASCADE,
    FOREIGN KEY (song_id)
        REFERENCES Songs(song_id)
        ON DELETE CASCADE
);


CREATE TABLE Listening_History (
    history_id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL,
    song_id INT NOT NULL,
    played_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id)
        REFERENCES Users(user_id)
        ON DELETE CASCADE,
    FOREIGN KEY (song_id)
        REFERENCES Songs(song_id)
        ON DELETE CASCADE
);


SHOW TABLES;
