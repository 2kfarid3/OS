#include <stdio.h>
#include <unistd.h>
#include <stdlib.h>
#include <sys/ipc.h>      // IPC açarı yaratmaq üçün
#include <sys/shm.h>      // Shared memory üçün funksiyalar
#include <sys/sem.h>      // Semaphore-lar üçün
#include "common.h"       // Bizim sabitləri saxlayan header faylı
int main() {
    // Mövcud shared memory-ə qoşul
    int shmid = shmget(SHM_KEY, SHM_SIZE, 0666);
    char *shm = (char *)shmat(shmid, NULL, 0);
// Mövcud shared memory-ə qoşulur (IPC_CREAT yoxdur, çünki oxuyur).
// Qoşulduqdan sonra shm dəyişəni həmin sahəni göstərir.


    // Mövcud semaphore-a qoşul
    int semid = semget(SEM_KEY, 1, 0666);
   // Mövcud semaphore tapılır

    struct sembuf p = {0, -1, 0}; // P əməliyyatı - lock
    struct sembuf v = {0, 1, 0};  // V əməliyyatı - unlock

    while (1) {
        semop(semid, &p, 1); // Lock
        printf("Reader: %s", shm);
        semop(semid, &v, 1); // Unlock
        sleep(1);
// Reader hər saniyə məlumatı oxuyur və ekrana çap edir.
// Oxuma əməliyyatı zamanı semaphore kilidini alır və sonra açır ki, yazı zamanı toqquşma // olmasın.
    }

    shmdt(shm);
    return 0;
}
