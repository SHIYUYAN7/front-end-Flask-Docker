CREATE TABLE IF NOT EXISTS `blockchain` (
`blockchain_id`      int(11)  	   NOT NULL auto_increment	  COMMENT 'blockchain_id',
`image_id`           int(11)  	   NOT NULL             	  COMMENT 'the id of this image',
`chain`              varchar(500)  NOT NULL                   COMMENT 'the chain',
PRIMARY KEY (`blockchain_id`),
FOREIGN KEY (image_id) REFERENCES images(image_id)
) ENGINE=InnoDB AUTO_INCREMENT=1 DEFAULT CHARSET=utf8mb4 COMMENT="Contains blockchain";