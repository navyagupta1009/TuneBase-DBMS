
USE TuneBase;

-- Q1. Display all songs
SELECT * FROM Songs;

-- Q2. Find songs of a particular genre
SELECT song_title, genre
FROM Songs
WHERE genre = 'Pop';

-- Q3. Display songs from shortest to longest
SELECT song_title, duration_seconds
FROM Songs
ORDER BY duration_seconds ASC;

-- Q4. Search for a song by title
SELECT *
FROM Songs
WHERE song_title LIKE '%Night%';

-- Q5. Display users who joined after a given date
SELECT username, join_date
FROM Users
WHERE join_date > '2026-01-31';


-- Q6. Display songs with their artists and albums
SELECT
    s.song_title,
    ar.artist_name,
    al.album_title,
    s.genre
FROM Songs s
JOIN Albums al ON s.album_id = al.album_id
JOIN Artists ar ON al.artist_id = ar.artist_id;

-- Q7. Display playlists with their owners
SELECT
    p.playlist_name,
    u.username
FROM Playlists p
JOIN Users u ON p.user_id = u.user_id;

-- Q8. Display songs in each playlist
SELECT
    p.playlist_name,
    s.song_title
FROM Playlist_Songs ps
JOIN Playlists p ON ps.playlist_id = p.playlist_id
JOIN Songs s ON ps.song_id = s.song_id
ORDER BY p.playlist_name;

-- Q9. Display users and the songs they like
SELECT
    u.username,
    s.song_title
FROM Likes l
JOIN Users u ON l.user_id = u.user_id
JOIN Songs s ON l.song_id = s.song_id;


-- Q10. Count songs by genre
SELECT genre, COUNT(*) AS total_songs
FROM Songs
GROUP BY genre;

-- Q11. Count songs in each album
SELECT
    al.album_title,
    COUNT(s.song_id) AS total_songs
FROM Albums al
LEFT JOIN Songs s ON al.album_id = s.album_id
GROUP BY al.album_id, al.album_title;

-- Q12. Find the average song duration
SELECT AVG(duration_seconds) AS average_duration
FROM Songs;

-- Q13. Find the most-played songs
SELECT
    s.song_title,
    COUNT(h.history_id) AS play_count
FROM Songs s
LEFT JOIN Listening_History h ON s.song_id = h.song_id
GROUP BY s.song_id, s.song_title
ORDER BY play_count DESC, s.song_title;


-- Q14. Find artists with more than one album
SELECT
    ar.artist_name,
    COUNT(al.album_id) AS album_count
FROM Artists ar
JOIN Albums al ON ar.artist_id = al.artist_id
GROUP BY ar.artist_id, ar.artist_name
HAVING COUNT(al.album_id) > 1;

-- Q15. Find songs longer than the average duration
SELECT song_title, duration_seconds
FROM Songs
WHERE duration_seconds > (
    SELECT AVG(duration_seconds)
    FROM Songs
);

-- Q16. Find users who have liked at least one song
SELECT username
FROM Users
WHERE user_id IN (
    SELECT user_id
    FROM Likes
);

-- Q17. Find songs that have never been played
SELECT song_title
FROM Songs
WHERE song_id NOT IN (
    SELECT song_id
    FROM Listening_History
);


-- Q18. Create a view of songs and artists
CREATE OR REPLACE VIEW SongDetails AS
SELECT
    s.song_id,
    s.song_title,
    ar.artist_name,
    al.album_title,
    s.genre,
    s.duration_seconds
FROM Songs s
JOIN Albums al ON s.album_id = al.album_id
JOIN Artists ar ON al.artist_id = ar.artist_id;

-- Use the view
SELECT * FROM SongDetails;


-- Q19. Update a song's genre
UPDATE Songs
SET genre = 'Pop'
WHERE song_id = 1;

-- Q20. Demonstrate a transaction
START TRANSACTION;

UPDATE Songs
SET genre = 'TestGenre'
WHERE song_id = 1;

SELECT song_id, song_title, genre
FROM Songs
WHERE song_id = 1;

ROLLBACK;

-- The original genre is restored
SELECT song_id, song_title, genre
FROM Songs
WHERE song_id = 1;
