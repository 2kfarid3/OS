#include <stdio.h>        
#include <stdlib.h>       // malloc, exit və s. üçün
#include <string.h>       // string funksiyaları üçün (fgets və s.)
#include <sys/ipc.h>      // IPC açarı yaratmaq üçün
#include <sys/shm.h>      // Shared memory üçün funksiyalar
#include <sys/sem.h>      // Semaphore-lar üçün
#include "common.h"       // Sabitləri saxlayan header faylı

int main() {
    // Shared memory yaradılır
    int shmid = shmget(SHM_KEY, SHM_SIZE, IPC_CREAT | 0666);
  // shmget() funksiyası ilə shared memory sahəsi yaradılır
 // SHM_KEY: unikal açar (eyni key reader ilə eyni olmalıdır)
 // SHM_SIZE: bölüşüləcək yaddaş ölçüsü
 // IPC_CREAT | 0666: əgər yoxdur isə yarat və read/write icazələri ver

    char *shm = (char *)shmat(shmid, NULL, 0);
 // shmat() funksiyası ilə yaradılmış yaddaş sahəsi prosesə qoşulur.
 // shm göstəricisi bu sahəni göstərir.


    // Semaphore yaradılır
    int semid = semget(SEM_KEY, 1, IPC_CREAT | 0666);
  // semget() ilə bir dənə semaphore yaradılır (və ya qoşulur).
 // SEM_KEY: eyni açar reader.c ilə uyğun olmalıdır.


    // Semaphore başlanğıc dəyəri 1 qoyulur
    semctl(semid, 0, SETVAL, 1);
  // semctl() ilə semaphore-a başlanğıc dəyər 1 təyin olunur.
 // 1 o deməkdir ki, resurs (shared memory) hazırda azaddır.


    struct sembuf p = {0, -1, 0}; // P əməliyyatı
    struct sembuf v = {0, 1, 0};  // V əməliyyatı
//  Bunlar semaphore əməliyyatları üçün strukturlardır.
//  p semaphore dəyərini 1 azaldır (yəni kilidləyir).
//  v isə artırır (kilidi açır).


    while (1) {
        printf("Yazmaq istədiyiniz mətni daxil edin: ");
        fgets(shm, SHM_SIZE, stdin);
// İstifadəçidən məlumat alınır və birbaşa shared memory-ə yazılır (shm).

        semop(semid, &p, 1); // Lock (semaphore)
        // Məlumat artıq shared memory-dədir
        semop(semid, &v, 1); // Unlock
    }

    shmdt(shm); // Yaddaşı detach etmək üçün (heç vaxt buraya gəlmir çünki sonsuz dövrdür)
    return 0;
}
