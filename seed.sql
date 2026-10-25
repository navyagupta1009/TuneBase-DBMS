
USE TuneBase;


INSERT INTO Users
(user_id, username, email, password_hash, join_date)
VALUES
(1, 'Aarav', 'aarav@example.com', 'SEED_ONLY_NOT_A_LOGIN_HASH', '2026-01-10'),
(2, 'Priya', 'priya@example.com', 'SEED_ONLY_NOT_A_LOGIN_HASH', '2026-01-15'),
(3, 'Rohan', 'rohan@example.com', 'SEED_ONLY_NOT_A_LOGIN_HASH', '2026-02-01'),
(4, 'Ananya', 'ananya@example.com', 'SEED_ONLY_NOT_A_LOGIN_HASH', '2026-02-12'),
(5, 'Kabir', 'kabir@example.com', 'SEED_ONLY_NOT_A_LOGIN_HASH', '2026-03-05');

-- 2. Artists
INSERT INTO Artists (artist_id, artist_name, country)
VALUES
(1, 'Enhypen', 'South Korea'),
(2, 'Taylor Swift', 'USA'),
(3, 'The Weeknd', 'Canada'),
(4, 'A. R. Rahman', 'India'),
(5, 'Coldplay', 'United Kingdom');

-- 3. Albums
INSERT INTO Albums
(album_id, album_title, release_date, artist_id)
VALUES
(1, 'DARK BLOOD', '2023-05-22', 1),
(2, '1989', '2014-10-27', 2),
(3, 'After Hours', '2020-03-20', 3),
(4, 'Dil Se..', '1998-07-08', 4),
(5, 'Parachutes', '2000-07-10', 5),
(6, 'A Rush of Blood to the Head', '2002-08-26', 5);

-- 4. Songs
INSERT INTO Songs
(song_id, song_title, duration_seconds, genre, album_id)
VALUES
(1, 'Bite Me', 167, 'K-pop', 1),
(2, 'Sacrifice(Eat Me Up)', 192, 'K-pop', 1),
(3, 'Blank Space', 231, 'Pop', 2),
(4, 'Style', 231, 'Pop', 2),
(5, 'Blinding Lights', 200, 'Synth-pop', 3),
(6, 'Save Your Tears', 215, 'Synth-pop', 3),
(7, 'Chaiyya Chaiyya', 407, 'Soundtrack', 4),
(8, 'Jiya Jale', 309, 'Soundtrack', 4),
(9, 'Yellow', 266, 'Alternative Rock', 5),
(10, 'Trouble', 273, 'Alternative Rock', 5),
(11, 'The Scientist', 309, 'Alternative Rock', 6),
(12, 'Clocks', 307, 'Alternative Rock', 6);

-- 5. Playlists
INSERT INTO Playlists
(playlist_id, playlist_name, user_id)
VALUES
(1, 'Chill Vibes', 1),
(2, 'Workout Mix', 1),
(3, 'Late Night Songs', 2),
(4, 'My Favorites', 3),
(5, 'Acoustic Mood', 4);

-- 6. Playlist_Songs
INSERT INTO Playlist_Songs (playlist_id, song_id)
VALUES
(1, 1), (1, 3), (1, 9), (1, 11),
(2, 5), (2, 7), (2, 10),
(3, 2), (3, 5), (3, 6),
(4, 1), (4, 7), (4, 12),
(5, 9), (5, 11), (5, 12);

-- 7. Likes
INSERT INTO Likes (user_id, song_id)
VALUES
(1, 1), (1, 3), (1, 7),
(2, 2), (2, 5), (2, 9),
(3, 1), (3, 6), (3, 12),
(4, 4), (4, 9), (4, 11),
(5, 3), (5, 7), (5, 10);

-- 8. Listening_History
INSERT INTO Listening_History
(history_id, user_id, song_id, played_at)
VALUES
(1, 1, 1, '2026-03-10 09:15:00'),
(2, 1, 3, '2026-03-10 09:20:00'),
(3, 1, 1, '2026-03-11 18:30:00'),
(4, 2, 5, '2026-03-11 20:00:00'),
(5, 2, 2, '2026-03-12 08:10:00'),
(6, 3, 7, '2026-03-12 15:30:00'),
(7, 3, 1, '2026-03-13 10:00:00'),
(8, 4, 9, '2026-03-13 21:45:00'),
(9, 4, 11, '2026-03-14 07:30:00'),
(10, 5, 10, '2026-03-14 19:15:00'),
(11, 1, 7, '2026-03-15 12:00:00'),
(12, 2, 5, '2026-03-15 22:00:00'),
(13, 3, 12, '2026-03-16 11:30:00'),
(14, 5, 3, '2026-03-16 17:20:00'),
(15, 1, 1, '2026-03-17 08:00:00');

-- Verify inserted data
SELECT 'Users' AS table_name, COUNT(*) AS total FROM Users
UNION ALL
SELECT 'Artists', COUNT(*) FROM Artists
UNION ALL
SELECT 'Albums', COUNT(*) FROM Albums
UNION ALL
SELECT 'Songs', COUNT(*) FROM Songs
UNION ALL
SELECT 'Playlists', COUNT(*) FROM Playlists
UNION ALL
SELECT 'Playlist_Songs', COUNT(*) FROM Playlist_Songs
UNION ALL
SELECT 'Likes', COUNT(*) FROM Likes
UNION ALL
SELECT 'Listening_History', COUNT(*) FROM Listening_History;
