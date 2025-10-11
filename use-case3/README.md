# use case 3

Target version of centos is 2009   (/09/2020) 
ansible version is v2.9.13 (1/09/2020)
python3  is 3.5.10 (05/09/2020)
python  is 2.7.5

## install ansible
```shell
 python3 -m venv venv
source venv/bin/activate
python -V
pip3 install ansible
python3 -m pip install --upgrade pip
ansible --version 
```
## latest ansible version from source
```shell
cd 
git clone https://github.com/ansible/ansible.git
git checkout tags/v2.19.1
git log --oneline
python3 -m venv ansible_latest
source ansible_latest/bin/activate
pip3 install -r requirements.txt
export PYTHONPATH=~/ansible/lib:$PYTHONPATH
export PATH=~/ansible/bin:$PATH
python -V
```