---
layout:     post
title:      "OS Project2 -- Simple Shell"
author:     "dusmart"
tags:
    - project
---

> A simple shell with history feature.

<!--more-->

---

## Feature

1. execute normal executable commands in **COMMAND** mode
2. execute command in background if a command end with ' &'
3. output most recent 10 commands and enter **HISTORY** mode when user enters \<Control\>\<C\>
4. execute history command in **HISTORY** mode when user enter 'r x', 'x' is the first letter of that command

## Outline

```
char history[HISTORY_NUM][MAX_LINE];
int history_index = 0;

int setup(char inputBuffer[], char *args[], int *background);
void execute(char *args[], const int background);
void handle_SIGINT(int sig);
int main();
```

1. ```char history[10][80]``` stores all infomation of last 10 commands entered by user
2. ```int history_index``` indicate which history is the last command
3. ```setup()``` take inputBuffer's command, separating it into distinct tokens using white space as delimiters. ```setup()``` modifies the args parameters so that it holds pointers to every tokens in inputBuffer. 
4. ```execute()``` take parsed command, executing it in child process and deciding whether or not suspend the main process

## main function

1. initialize variables
2. set up the signal handler
3. enter the main loop: read command and call setup() and execute()
```
int main(){
    // initialize variables
    char inputBuffer[MAX_LINE];
    int length, background;
    char *args[MAX_LINE/2 + 1];
    // set up the signal handler
    struct sigaction handler;
    handler.sa_handler = handle_SIGINT;
    sigaction(SIGINT, &handler, NULL);

    // the main loop
    while(TRUE){
        printf(COLOE_LIGHT_BLUE"COMMAND >> "NONE);
        fflush(stdout);
        // read command
        if((length = read(STDIN_FILENO, inputBuffer, MAX_LINE)) == 0) exit(0);
        inputBuffer[length] = '\0';
        // parse the args in command and store right command to history
        setup(inputBuffer, args, &background);
        execute(args, background);
    }
    return 0;
}
```

## execute function

1. fork a child process
2. different procedure for child and parent

```
void execute(char *args[], const int background){
    // fork a child process to do the command
    pid_t pid = fork();
    if(pid < 0){
        // handle error
        fprintf(stderr, COLOR_PURPLE"Fork failed!\n"NONE);
        exit(-1);
    }
    else if(pid == 0){
        // child process
        if(execvp(args[0], args) == -1){
            printf(COLOR_PURPLE"Warning: There is no such instruction.\n"NONE);
        }
        exit(0);
    }
    else{
        //parent process
        if(background == FALSE){
            waitpid(pid, NULL, 0);
        }
    }
}
```

## handle_SIGINT function

1. output most recent 10 history
2. read command from **HISTORY** mode
3. different procedure for 'r x' and 'r' command, this part is the same as main function

```
void handle_SIGINT(int sig){
    char inputBuffer[MAX_LINE];
    char *args[MAX_LINE/2 + 1];
    int length, background;
    int i = (history_index<10)?0:(history_index-10);
    printf("\n");
    for(;i<history_index;++i){
        printf("%d: ", i+1);
        printf("%s", history[i%10]);
        fflush(stdout);
    }
    //execute history command
    printf(COLOR_LIGHT_CYAN"HISTORY >> "NONE);
    fflush(stdout);
    if((length = read(STDIN_FILENO, inputBuffer, MAX_LINE)) == 0) exit(0);
    while(inputBuffer[0] != 'r' && (length==2 || length==4)){
        printf(COLOR_PURPLE"Warning: You can only use 'r x' or 'r' format to call history commands.'x' is the first letter of that command.\n"NONE);
        printf(COLOR_LIGHT_CYAN"HISTORY >> "NONE);
        fflush(stdout);
        if((length = read(STDIN_FILENO, inputBuffer, MAX_LINE)) == 0) exit(0);
    }
    if(length == 2){
        printf("%s", history[(history_index-1)%10]);
        strcpy(inputBuffer, history[(history_index-1)%10]);
        setup(inputBuffer, args, &background);
        execute(args, background);
    }
    else if(inputBuffer[1] == ' '){
        for(i=history_index-1;i>=0&&i>=history_index-10;--i){
            if(history[i%10][0] == inputBuffer[2]) break;
        }
        printf("%s", history[i%10]);
        strcpy(inputBuffer, history[i%10]);
        setup(inputBuffer, args, &background);
        execute(args, background);
    }
    fflush(stdout);
}
```

## setup function

This part is provided in the book(OPERATING SYSTEM CONCEPTS --7th edition -- Page122)

I change it to support history feature. That is to say, when a command is parsed successfully, I add it to the history and update the history_index.

```
int setup(char inputBuffer[], char *args[], int *background){
    int i, start = -1, count = 0, length = strlen(inputBuffer);
    char tmp[MAX_LINE];
    *background = FALSE;
    memcpy(tmp, inputBuffer, MAX_LINE);
    for(i=0; i<length; ++i){
        switch(inputBuffer[i]){
            case ' ':
            case '\t':
                if(start != -1){
                    args[count] = &inputBuffer[start];
                    count++;
                }
                inputBuffer[i] = '\0';

                start = -1;
                break;
            case '\n':
                if(start != -1){
                    args[count] = &inputBuffer[start];
                    count++;
                }
                inputBuffer[i] = '\0';
                args[count] = NULL;
                break;
            default:
                if(start == -1) start = i;
                if(inputBuffer[i] == '&'){
                    *background = TRUE;
                    inputBuffer[i] = '\0';
                    start = -1;
                }
        }
    }
    args[count] = NULL;
    if(count != 0){
        memcpy(history[(history_index++)%10], tmp, MAX_LINE);
        return 0;
    }
    else return -1;
}
```

## source code and demo

[https://github.com/dusmart/simple_shell](https://github.com/dusmart/simple_shell)

![img](/assets/img/2017-03-11-1.png)