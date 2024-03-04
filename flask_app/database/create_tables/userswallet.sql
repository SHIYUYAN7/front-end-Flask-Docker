CREATE TABLE IF NOT EXISTS `userswallet` (
`userwallet_id`   int(11)  	   NOT NULL auto_increment	  COMMENT 'the id of this userwallet',
`user_id`         int(11)  	   NOT NULL              	  COMMENT 'the id of this user',
`user_key`        varchar(100) NOT NULL            		  COMMENT 'the user key',
`token`           int(11)      NOT NULL                   COMMENT 'the token',
PRIMARY KEY (`userwallet_id`),
FOREIGN KEY (user_id) REFERENCES users(user_id)
) ENGINE=InnoDB AUTO_INCREMENT=1 DEFAULT CHARSET=utf8mb4 COMMENT="Contains user wallet";