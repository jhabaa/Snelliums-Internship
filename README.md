# Snelliums-Internship
### Mission
> Ok. Here is the topic. I have a camera made by Blaster. The main idea is to connect more than one camera to an Arduino, and take a picture simultaneously on all connected cameras. 
Then analyse all those pictures and give a rate. That's all for the first mission. the second and the third ones are the Arduino config (With an ADC maybe to get the good time to shoot) and an interface to show pictures and save them easily.

./scripts/apply-code-style.sh 

cmake -S /home/snellium/Documents/JH/daemon/ -DMODULES="all" -DENABLE_UEYE="off" -DENABLE_LICENCE_CHECK="off" -DCMAKE_CUDA_FLAGS="--compiler-bindir=/usr/bin/g++-9" -B /home/snellium/Documents/JH/daemon-compiled

make -j
