CREATE TABLE IF NOT EXISTS `images` (
`image_id`        int(11)  	   NOT NULL             	  COMMENT 'the id of this image',
`owner`           int(11)  	   NOT NULL              	  COMMENT 'the owen of this image which is id of this user',
`token`           int(11)      NOT NULL            		  COMMENT 'the token of image',
`description`     varchar(256) NOT NULL                   COMMENT 'the description',
PRIMARY KEY (`image_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT="Contains NFT images";