# Install dddm on a linux environment

# Installing multinest
echo "do install of multinest"
echo $LD_LIBRARY_PATH
sudo apt-get install -qq libblas{3,-dev} liblapack{3,-dev} cmake build-essential git gfortran
sudo apt-get install -qq openmpi-bin libopenmpi-dev python-mpi4py
echo "doing pip install"
echo "cloning dir"
git clone https://github.com/JohannesBuchner/MultiNest
mkdir -p MultiNest/build; pushd MultiNest/build; cmake .. && make && popd
test -e MultiNest/lib/libmultinest.so
pip install pymultinest

echo "set LD_LIBRARY_PATH to" $LD_LIBRARY_PATH
echo "in that folder is:"

ls $LD_LIBRARY_PATH ; echo $LD_LIBRARY_PATH
echo "go back to installation; ls ; pwd "

cd DirectDmTargets
echo "done"
