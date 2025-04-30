Code Explanation:
Usage of Shared Memory
Shared memory is a highly efficient Inter-Process Communication (IPC) mechanism that allows multiple processes to access a common region of physical memory for direct data exchange. In this project, shared memory was created using the shmget() function and then attached to the process using shmat(). Compared to file or socket-based communication, shared memory provides much faster data transmission as it avoids overhead from disk access or kernel-space buffering.

The writer process (writer.c) receives input from the user and writes it directly into the shared memory region. The reader process (reader.c) connects to the same memory region using a shared SHM_KEY and reads the data in real time. This approach is commonly used in real-world systems such as multi-core processors, database systems, and multimedia applications where fast and synchronized communication is required.

However, one of the main challenges with shared memory is synchronization. If two or more processes access the memory simultaneously, a race condition or data corruption can occur. To prevent this, an additional synchronization mechanism—semaphore—is used in this project.

🔹 Usage of Semaphore
A semaphore is a basic synchronization primitive that regulates access to a critical section shared by multiple processes. In this project, a semaphore was created using the semget() function, initialized with semctl(), and managed with the semop() function.

Before reading or writing to the shared memory, both the writer and reader perform a P operation (decrement the semaphore) to lock the resource, and a V operation (increment the semaphore) to unlock it once their operation is complete. This ensures mutual exclusion, meaning only one process can access the shared memory at a time.

Without semaphores, both processes could try to access or modify the shared data concurrently, leading to inconsistent or corrupted results. By using semaphores, we guarantee that the communication is safe, atomic, and predictable.

🔹 Conclusion and Advantages
By combining shared memory with semaphores, this project successfully implements efficient and secure data transfer between two concurrent processes. The main advantages of this approach include:

High transmission speed (due to direct memory access),

Simple and effective design for two-way communication,

Safe synchronization via semaphores to protect data consistency,

And suitability for Unix/Linux environments where IPC is widely used.

This implementation demonstrates core concepts of IPC and multi-process programming, helping to understand real-world synchronization challenges and how to overcome them using classic operating system mechanisms.

Kod Izahı:
Shared Memory istifadəsi
Shared memory (ümumi yaddaş) – bir neçə prosesin eyni fiziki yaddaş sahəsini paylaşaraq bir-biri ilə birbaşa məlumat mübadiləsi aparmasına imkan verən yüksək səmərəli IPC mexanizmidir. Bu layihədə shared memory shmget() funksiyası vasitəsilə yaradılmış və shmat() ilə prosesə qoşulmuşdur. Bu yanaşma, fayl və ya soket vasitəsilə məlumat ötürülməsindən daha sürətli işləyir, çünki əlavə disk və ya kernel-nüvəsi səviyyəsində gecikmələr baş vermir.

Mənbə proses (writer.c) istifadəçidən daxil edilən məlumatı bu sahəyə yazır. Digər proses (reader.c) isə eyni yaddaş sahəsinə qoşularaq məlumatı oxuyur. Hər iki proses eyni SHM_KEY istifadə etdiyinə görə eyni yaddaş sahəsinə çıxış əldə edirlər. Bu, bir çox real həyati sistemlərdə – məsələn, çox nüvəli prosessorlu sistemlərdə, verilənlər bazası idarəetmə sistemlərində və multimedia tətbiqlərində geniş istifadə olunur.

Lakin shared memory istifadəsində əsas çətinlik sinxronlaşdırmadır. Əgər iki və ya daha çox proses eyni anda bu sahəyə daxil olarsa, "race condition" və ya məlumat zədələnməsi (data corruption) baş verə bilər. Məhz bu səbəbdən bu layihədə əlavə olaraq semaphore mexanizmi istifadə olunmuşdur.

🔹 Semaphore istifadəsi
Semaphore – bir və ya bir neçə prosesin kritik sahəyə girişini idarə etmək üçün istifadə olunan sadə sinxronizasiya obyektidir. Layihədə semget() funksiyası ilə semaphore yaradılmış, semctl() ilə başlanğıc dəyəri təyin olunmuş və semop() funksiyası ilə idarə edilmişdir.

writer.c və reader.c proqramları məlumat yazmadan və oxumadan əvvəl semaphore dəyərini 1 azaldır (P əməliyyatı) və sonra işi bitirdikdə yenidən artırır (V əməliyyatı). Bu yanaşma kritik sahənin kilidlənməsi və sərbəst buraxılması kimi işləyir və eyni anda yalnız bir prosesin shared memory sahəsinə daxil olmasına imkan yaradır.

Semaphore istifadə olunmasaydı, həm writer, həm də reader eyni anda shm sahəsinə müdaxilə edə bilərdi və nəticədə qarışıq, zədələnmiş və ya natamam məlumatlar oxuna bilərdi. Bu tip təhlükəli vəziyyətlərə qarşı semaphore mexanizmi layihədə təhlükəsizlik və düzgünlük təminatçısı kimi çıxış edir.

🔹 Nəticə və üstünlüklər
Layihədə shared memory və semaphore birlikdə istifadə edilərək çox prosesli mühitdə məlumat ötürülməsi uğurla həyata keçirilmişdir. Bu yanaşma aşağıdakı üstünlükləri təmin edir:

Yüksək ötürmə sürəti (çünki kernel və ya fayl sistemi istifadə olunmur).

Sadə və effektiv dizayn (iki proses arasında birbaşa ünsiyyət).

Synchronization (semaphore vasitəsilə idarə olunma) sayəsində məlumat bütövlüyü və ardıcıllıq təmin edilir.

Unix/Linux əməliyyat sistemləri üçün ideal IPC təcrübəsi təqdim edir.

Bu layihə, əsas IPC texnikalarını praktik şəkildə öyrənmək, çox prosesli proqramlaşdırma prinsiplərini dərk etmək və real sistemlərdə qarşılaşılan sinxronizasiya problemlərini həll etmək üçün əhəmiyyətli bir nümunədir.
