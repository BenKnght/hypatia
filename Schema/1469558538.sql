ALTER TABLE `star` CHANGE `uvw` `u` FLOAT NULL DEFAULT NULL;
ALTER TABLE `star` ADD `v` FLOAT NULL AFTER `u`, ADD `w` FLOAT NULL AFTER `v`;
ALTER TABLE `star` CHANGE `position` `x` FLOAT(32) NULL DEFAULT NULL COMMENT 'Position converts the polar coordinates, namely RA, Dec, and dist, to rectangular coordinates, where the Sun is at the center';
ALTER TABLE `star` CHANGE `x` `x` FLOAT NULL DEFAULT NULL COMMENT 'Position converts the polar coordinates, namely RA, Dec, and dist, to rectangular coordinates, where the Sun is at the center';
ALTER TABLE `star` ADD `y` FLOAT NULL COMMENT 'Position converts the polar coordinates, namely RA, Dec, and dist, to rectangular coordinates, where the Sun is at the center' AFTER `x`, ADD `z` FLOAT NULL COMMENT 'Position converts the polar coordinates, namely RA, Dec, and dist, to rectangular coordinates, where the Sun is at the center' AFTER `y`;
