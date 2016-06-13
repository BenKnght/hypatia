-- Add Solar Normalization column in composition table

ALTER TABLE `composition` ADD `solarnorm` CHAR(64) NOT NULL FIRST;
ALTER TABLE `composition` DROP PRIMARY KEY, ADD PRIMARY KEY( `solarnorm`, `hip`, `cid`, `element`);

