


# PWDLv3 - pw.live Downloader  Version 3

## History 
This project started way back in 2023 as [pwdl](https://github.com/shubhamakshit/pwdl). It was then merely a script for downloading segments using a loophole in pw's api. When it got pached we moved on to [pwdlv2](https://github.com/shubhamakshit/pwdlv2) in March, 2024. It was mostly haphazard code. pwdlv3 started in April, 2024 as is proudly growing ever since.

## UPDATE: RE-INSTALL PWDL POST 12th JUN 2025

## Installing guide 

### Windows (64bit)
Open Powershell as **Administrator**
```powershell
irm https://raw.githubusercontent.com/shubhamakshit/pwdlv3_assets/main/dl.pwdlv3.ps1 | iex
```

### Linux (64bit)
```bash
git clone https://github.com/shubhamakshit/pwdlv3.git
cd pwdlv3
chmod +x ./setup.sh
./setup.sh -f # -f means ffmpeg ; (ffmpeg binary in PATH is given preference)
source ~/.bashrc
```
## Getting started 
### Logging in 
For *more* interactive login
```bash
pwdl --login 
```
For  *less* interactive login
**Tip** :  Prepend the phone number by `wa` for whatsapp OTP.
```bash
pwdl --phone waXXXXXXXXXX # or pwdl --phone XXXXXXXXXX
```
### Starting webui 
The webui as of May, 2025 has moved to [pwdl-webui.vercel.app](https://pwdl-webui.vercel.app). The backend however must be on your local machine.
```bash
pwdl --webui
```
1. Look for a url with a port number (default:**5000**)
![445214262-64343af7-bad5-4fcb-b600-1ac95b710b9f](https://github.com/user-attachments/assets/4c3dfb35-dd57-4386-bac9-e2a6671b7b8e)

2. Open that url. In most cases [localhost:5000](http://localhost:5000).
![image](https://github.com/user-attachments/assets/c1a8cfef-78d5-4d89-b76a-74c4b69e1671)

3. Open the Online WebUI. As of now [pwdl-webui.vercel.app](https://pwdl-webui.vercel.app).
![image](https://github.com/user-attachments/assets/44aae130-3803-4a5c-ad49-9e2601ac3e82)

    1. Open Settings -> WebSettings Click on Edit and change the API value to the url obtained in 2.
       ![image](https://github.com/user-attachments/assets/62aec806-b4ea-48a3-bda0-944c601408fd)
    2. Explore other values of Web Settings to get your desired value.
    3. Open 'BOSS' (Library) and Enjoy 
