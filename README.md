This code is used to get parameters of earthquake from short messages
that used by BMKG, Indonesia. Those parameters are origin time,
magnitude, latitude, longitude, depth, and location remarks.
The code written by shyogaswara, for further information please mail me 
at sh.yogaswara@gmail.com

[PYTHON VERSION]
3.10

[LIBRARIES]
datetime
re

[MOIDULES]
day_translator (github/shyogaswara)


[CHANGELOG 1/2024]
- rewrite all function from previous release into GetParam class
- remove the function to split text that depend on their origin
