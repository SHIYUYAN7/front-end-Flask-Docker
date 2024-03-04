CREATE TABLE IF NOT EXISTS `transactions` (
`transaction_id`         int(11)  	    NOT NULL auto_increment	  COMMENT 'the id of this transaction',
`chain_index`            int(11)        NOT NULL                  COMMENT 'index',
`timestamp`              datetime       NOT NULL                  COMMENT 'timestamp',
`cost`                   int(11)        NOT NULL                  COMMENT 'cost',
`seller_id`              varchar(20)    NOT NULL                  COMMENT 'seller_id',
`buyer_id`               varchar(20)    NOT NULL                  COMMENT 'buyer_id',
`current_owner`          varchar(20)    NOT NULL                  COMMENT 'current_owner',
`image_id`               int(11)        NOT NULL                  COMMENT 'image_id',
`previous_hash`          varchar(256)   NOT NULL                  COMMENT 'previoushash',
`workproof`              int(11)        NOT NULL                  COMMENT 'workproof',
PRIMARY KEY (`transaction_id`)
) ENGINE=InnoDB AUTO_INCREMENT=1 DEFAULT CHARSET=utf8mb4 COMMENT="Contains transactions";
