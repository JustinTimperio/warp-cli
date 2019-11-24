## Performance Gains
Below are timed downloads(in seconds) over my personal network which is 1 Gigabit. Each progressive transfer increases the total size of the transfer in GB, while reducing the total number of files being transferred. WDT easily maintains near full 1 Gigabit saturation across all 3 transfers while HPN-SFTP and SSH struggle to transfer multiple small files(single-thread limited). With encryption disabled HPN-SSH reaches full saturation when transferring large files, while stock SSH continues to struggle under heavy load. If you have access to +10 Gigabit networking hardware you can expect WDT to scale to ~40 Gigabit and HPN-SSH to scale to ~10 Gigabit.

![Performance Graph](https://i.imgur.com/ax7eKzj.png)
