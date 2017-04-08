#include <stdlib.h>
#include <stdio.h>
#include <time.h>
#include <pthread.h>
#include <semaphore.h>
#include <unistd.h>

#define BUFFER_SIZE 5
#define TRUE 1
#define FALSE 0

typedef int buffer_item;
buffer_item buffer[BUFFER_SIZE];
pthread_mutex_t mutex;
sem_t full;
sem_t empty;
int start;
int end;

int insert_item(buffer_item item){
    int pos;
    sem_wait(&empty);
    pthread_mutex_lock(&mutex);
    pos = start;
    start = (start + 1)%BUFFER_SIZE;
    pthread_mutex_unlock(&mutex);
    sem_post(&full);
    buffer[pos] = item;
    return 0;
}

int remove_item(buffer_item *item){
    int pos;
    sem_wait(&full);
    pthread_mutex_lock(&mutex);
    pos = end;
    end = (end + 1)%BUFFER_SIZE;
    pthread_mutex_unlock(&mutex);
    sem_post(&empty);
    *item = buffer[pos];
    return 0;
}

void *producer(void *param){
    buffer_item rand_item;
    while(TRUE){
        // sleep for a random period of time
        usleep(rand()%1000000);
        // generate a random number
        rand_item = rand();
        printf("producer[%d]\tproduced\t%d\n", *(int *)param, rand_item);
        if(insert_item(rand_item)){
            fprintf(stderr, "report error condition\n");
        }
    }
}

void *consumer(void *param){
    buffer_item rand_item;
    while(TRUE){
        // sleep for a random period of time
        usleep(rand()%1000000);
        // generate a random number
        rand_item = rand();
        if(remove_item(&rand_item))
            fprintf(stderr, "report error condition\n");
        else
            printf("consumer[%d]\tconsumed\t%d\n", *(int *)param ,rand_item);
    }
}

int main(int argc, char *argv[]){
    // 1. get command line arguments
    srand((unsigned)time(NULL));
    int producer_num,consumer_num,run_time;
    run_time=atoi(argv[1]);
    producer_num=atoi(argv[2]);
	consumer_num=atoi(argv[3]);
    // 2. initialize buffer
    pthread_mutex_init(&mutex,NULL);
    sem_init(&full,0,0);
    sem_init(&empty,0,BUFFER_SIZE);
    start = end = 0;
    // 3. create producer threads
    pthread_t *producer_t = (pthread_t *)malloc(producer_num*sizeof(pthread_t));
    int *producer_id = (int *)malloc((producer_num+1)*sizeof(int));
    for(int i=0; i<producer_num; ++i, producer_id[i]=i)
        pthread_create(&producer_t[i], NULL, producer, &producer_id[i+1]);
    // 4. create consumer threads
    pthread_t *consumer_t = (pthread_t *)malloc(consumer_num*sizeof(pthread_t));
    int *consumer_id = (int *)malloc((consumer_num+1)*sizeof(int));
    for(int i=0; i<consumer_num; ++i, consumer_id[i]=i)
        pthread_create(&consumer_t[i], NULL, consumer, &consumer_id[i+1]);
    // 5. sleep
    sleep(run_time);
    // 6. exit
    return 0;
}