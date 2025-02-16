SET autocommit=0;

START TRANSACTION;

CREATE TABLE IF NOT EXISTS `scraper_states` (
	`id` int(11) NOT NULL AUTO_INCREMENT,
	`name` varchar(150) NOT NULL,
	`enabled` int(11) NOT NULL DEFAULT '1',
	PRIMARY KEY (`id`),
	UNIQUE KEY `name_UNIQUE` (`name`)
);

CREATE TABLE IF NOT EXISTS `scraper_stats` (
	`id` int(11) NOT NULL AUTO_INCREMENT,
	`service` varchar(150) DEFAULT NULL,
	`host` varchar(150) DEFAULT NULL,
	`attempts` FLOAT NOT NULL DEFAULT '0',
	`resolved` FLOAT NOT NULL DEFAULT '0',
	`success` FLOAT NOT NULL DEFAULT '0',
	PRIMARY KEY (`id`),
	UNIQUE KEY `service_UNIQUE` (`service`,`host`)
);

CREATE TABLE IF NOT EXISTS `search_cache` (
	`cache_id` int(11) NOT NULL AUTO_INCREMENT,
	`hash` varchar(255) NOT NULL,
	`service` varchar(45) NOT NULL,
	`host` varchar(45) NOT NULL,
	`display` varchar(255) NOT NULL,
	`quality` int(11) DEFAULT '3',
	`url` varchar(255) NOT NULL,
	`ts` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
	PRIMARY KEY (`cache_id`)
);

CREATE TABLE IF NOT EXISTS `playback_states` (
	`id` int(11) NOT NULL AUTO_INCREMENT,
	`imdb_id` varchar(45) DEFAULT NULL,
	`season` int(11) DEFAULT '0',
	`episode` int(11) DEFAULT '0',
	`current` varchar(45) DEFAULT NULL,
	`total` varchar(45) DEFAULT NULL,
	PRIMARY KEY (`id`),
	UNIQUE KEY `imdb_id_UNIQUE` (`imdb_id`,`season`,`episode`)
);

CREATE TABLE IF NOT EXISTS `host_weights` (
	`id` int(11) NOT NULL AUTO_INCREMENT,
	`host` varchar(150) DEFAULT NULL,
	`weight` int(11) DEFAULT '1000',
	`disabled` tinyint(1) DEFAULT '0',
	PRIMARY KEY (`id`),
	UNIQUE KEY `host_UNIQUE` (`host`)
);

CREATE OR REPLACE VIEW `fresh_cache` AS
	SELECT 
		`search_cache`.`cache_id` AS `cache_id`,
		`search_cache`.`hash` AS `hashid`,
		`search_cache`.`service` AS `service`,
		`search_cache`.`host` AS `host`,
		`search_cache`.`display` AS `title`,
		`search_cache`.`url` AS `url`,
		`search_cache`.`quality` AS `quality`,
		(timestampdiff(MINUTE, `search_cache`.`ts`, NOW()) > 120) AS `fresh`
	FROM `search_cache`
	WHERE (timestampdiff(MINUTE, `search_cache`.`ts`, NOW()) > 120)
;

CREATE OR REPLACE VIEW `stale_cache` AS
	SELECT 
		`search_cache`.`cache_id` AS `cache_id`,
		`search_cache`.`hash` AS `hashid`,
		(timestampdiff(MINUTE, `search_cache`.`ts`, NOW()) < 120) AS `stale`
	FROM `search_cache`
	WHERE (timestampdiff(MINUTE, `search_cache`.`ts`, NOW()) < 120)
;

CREATE OR REPLACE VIEW `host_ranks` AS
	SELECT host, 
	((1000 - weight) - (10000 * disabled)) as rank, 
	weight 
	FROM host_weights 
	WHERE ((1000 - weight) - (10000 * disabled)) >= 0 
	ORDER BY weight, host ASC
;

COMMIT;

SET autocommit=1;
