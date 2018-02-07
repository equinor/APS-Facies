/* lib_message*

________________________________________________________________

		lib_message
________________________________________________________________

Name:		lib_message.c - Source file
Description:    Library with functions for standarized error messages, 
                warnings and messages.

*/

/*Include Files:*/
#include <errno.h>
#include <string.h>
#include <stdio.h>

#include "lib_message.h"

/*  Local functions: */
static int checkLevels(int, int, int);
static void setStdErrors();
static void moduleUsage(char *, ...);

/* Initialization  of global varaibles: */

static char *progName;
static int progNameLength;
static char *usageTxt;
static char lastMessage[2048];
static char **stdError;
int noExitOnError=0;

/* Default values for output level: ERROR/WARNING/MESSAGE = 2
 
Level          0               1                   2       
----------------------------------------------------------------
ERROR:     errors_std     errors_std          errors_details

WARNINGS:     No          warning_serious     warning_all

MESSAGES:     No          message_some        message_details   

*/


static int errorLevel = 2;
static int warningLevel = 2;
static int messageLevel = 2;



/*F:initMessage*

________________________________________________________________

		initMessage
________________________________________________________________

Name:		initMessage
Syntax:		@initMessage-syntax
Description:    Initialize some global variables used in the functions
                moduleError, moduleWarning and moduleMessage.
		Parameters to the program calling this function may be: \\
                -usage : Print usage to screen \\
                -noExit: Do not exit on errors in the calling program \\
                -e level : Set error level, default value 2 \\
                -w level : Set warning level, default value 2 \\
                -m level : Set message level, default value 2 

Side effects: Global variables stdError, errorLevel, warningLevel and
              messageLevel is initialized. \\
              Exit errors



*/

/*<initMessage-syntax: */
void initMessage(int argc, char *argv[], char *usage) 
/*>initMessage-syntax: */ 
{
  char *ptr;
  int i,error;

  progName = (char *) calloc(15,sizeof(char));
  strcpy(progName,"(untitled)");
  
  usageTxt = (char *) calloc(15,sizeof(char));
  strcpy(usageTxt,"No usage");

  if (argc != 0) {
    progName = (char *) realloc(progName,(strlen(argv[0])+1)*sizeof(char));
    strcpy(progName,argv[0]);
    progNameLength = strlen(progName);
    ptr = usage;
    usageTxt = (char *) calloc(strlen(usage) + strlen(progName)+1,sizeof(char));
    sprintf(usageTxt, ptr, progName);
  

    for (i=1; i<=argc; i++) {
      if (argv[i]!=0) {
	if (strcmp(argv[i],"-usage") == 0)
	  moduleUsage(usageTxt);
	else if (strcmp(argv[i],"-noExit") == 0)
	  noExitOnError = 1;
	else if ((strcmp(argv[i],"-e") == 0) && i <  argc-1)
	  sscanf(argv[++i],"%d",&errorLevel);
	else if ((strcmp(argv[i],"-w") == 0) && i <  argc-1)
	  sscanf(argv[++i],"%d",&warningLevel);
	else if ((strcmp(argv[i],"-m") == 0) && i <  argc-1)
	  sscanf(argv[++i],"%d",&messageLevel);
      }
    }
  }

  error = checkLevels(errorLevel,warningLevel,messageLevel);
  if (error)  exit(1);

  /* set standard error messages */
  setStdErrors();

  return;
}	/* end of initMessage */





/*F:moduleError*

________________________________________________________________

		moduleError
________________________________________________________________

Name:		moduleError
Syntax:		@moduleError-syntax
Description:    Write error messages to stderr. \\
                If errorLevel = 1: Only standard message is printed\\
                If errorLevel = 2: Standard and detailed messages are printed\\

		Allowed values for errorNumber: \\
                NODEFAULT = No default message is printed \\
                OPENFILE  = Error opening file \\
                READFILE  = Error reading from file \\
                WRITEFILE = Error writing to file \\
		CLOSEFILE = Error closing a file \\
                ALLOC     = Unable  to allocat more space \\
                MODEL     = Error in specified  model \\
                KERNEL    = Internal module error (from kernel of program)

Side effects:   Exit program in not -noExit option is used. \\
                Print error message to stderr if errorNumber is illegal.
Return value: void
Global or static variables used: stdError, noExitOnError, errorLevel
*/

/*<moduleError-syntax: */
void moduleError(int errorNumber, const char *function, const char *format, ...)
/*>moduleError-syntax: */
{
  va_list ap;

  va_start(ap, format);



  if (errorLevel == 1 || errorLevel == 2) {
    fprintf(stderr,"\nERROR(%s,%s) ", progName,function);
    if (errorNumber != NODEFAULT) {
      sprintf(lastMessage,"    * ");
      sprintf(&lastMessage[6],"%s", stdError[errorNumber]);
      fprintf(stderr,"\n%s",lastMessage);
    }
  }
  if (errorLevel == 2) {
    sprintf(lastMessage,"    - ");
    vsprintf(&lastMessage[6], format, ap);
    fprintf(stderr,"\n%s\n",lastMessage);
    va_end(ap);
  }
  else
    fprintf(stderr,"\n");

  if (!noExitOnError)
    exit(1);        

  fflush(stderr);

  return;
}	/* end of moduleError */






/*F:modelFileError*

________________________________________________________________

		modelFileError
________________________________________________________________

Name:		modelFileError
Syntax:		@modelFileError-syntax
Description:    Write error messages to stderr. \\
                If errorLevel = 1: No error message is printed\\
                If errorLevel = 2: Detailed messages are printed\\

Return value: void
Global or static variables used: errorLevel
*/

/*<modelFileError-syntax: */
void modelFileError(char *format, ...)
/*>modelFileError-syntax: */
{
  va_list ap;

  va_start(ap, format);

  if (errorLevel == 2) {
    fprintf(stderr,"\nERROR(%s): ", progName);
    vsprintf(lastMessage, format, ap);
    fprintf(stderr,"%s",lastMessage);
    va_end(ap);
  }
               
  fflush(stderr);

  return;
}	/* end of modelFileError */









/*F:moduleWarning*

________________________________________________________________

		moduleWarning
________________________________________________________________

Name:		moduleWarning
Syntax:		@moduleWarning-syntax
Description:    Write warnings to stdout. \\
                If warningLevel = 0: No warnings \\
                If warningLevel = 1: Serious warnings \\
                If warningLevel = 2: All warnings \\
                \ \\
                Allowed values for warningType:\\ 
                CORRECT = Serious warning, should be corrected. \\
                CHECK   = Not serious, but should be checked.
Side effects:   Print error message to stderr if warningType illegal
Return value:   void
Global or static variables used: warningLevel
*/

/*<moduleWarning-syntax: */
void moduleWarning(int warningType, const char *function, const char *format, ...)
/*>moduleWarning-syntax: */
{ va_list ap;

  va_start(ap, format);

  if (warningType != CORRECT && warningType != CHECK)
    moduleError(NODEFAULT,"moduleWarning",
		"Warning must be of cathegory 'CORRECT' or 'CHECK");

  if (((warningLevel == 1) && (warningType == CORRECT)) ||
      ((warningLevel == 2) && (warningType == CORRECT || 
			       warningType ==CHECK))) { 
    fprintf(stdout,"\nWARNING(%s,%s) ", progName,function);
    sprintf(lastMessage,"    - ");
    vsprintf(&lastMessage[6], format, ap);
    if (fprintf(stdout,"\n%s\n",lastMessage) < 0)
    {
       fprintf(stderr, "Error writing warning: %s\n", strerror(errno));
       if (!noExitOnError)
       {
          exit(1);
       }
    }
    va_end(ap);
  }             
  
  fflush(stderr);

  return;
}	/* end of moduleWarning */








/*F:moduleMessage*

________________________________________________________________

		moduleMessage
________________________________________________________________

Name:		moduleMessage
Syntax:		@moduleMessage-syntax
Description:    Write messages to stdout. \\
                If messageLevel = 0: No messages \\
                If messageLevel = 1: Only runtime status \\
                If messageLevel = 2: Runtime status and detailed messages\\
                \ \\
                Allowed values for mesageType:\\ 
                STATUS    = Runtime message\\
                DETAILS   = Detailed message/information from program

Side effects:  Print error message to stderr if illegal messageType used
Return value:  void
Global or static variables used: messageLevel
*/

/*<moduleMessage-syntax: */
void moduleMessage(int messageType, const char *function, const char *format, ...)
/*>moduleMessage-syntax: */
{
  va_list ap;

  va_start(ap, format);
  

  if (messageType != STATUS && messageType != DETAILS)
    moduleError(NODEFAULT,"moduleMessage",
		"Message must be of cathegory 'STATUS' or 'DETAILS'");

  if ((messageLevel == 2 && (messageType == STATUS 
			     || messageType == DETAILS)) ||
      ((messageLevel == 1) && (messageType == STATUS))) {
    if (messageType == STATUS)
      fprintf(stdout,"\nMESSAGE(%s,%s) ", progName,function);
    sprintf(lastMessage,"    - ");
    vsprintf(&lastMessage[6], format, ap);
    if (fprintf(stdout,"\n%s\n",lastMessage) < 0)
    {
       fprintf(stderr, "Error writing message: %s\n", strerror(errno));
       if (!noExitOnError)
       {
          exit(1);
       }
    }
    va_end(ap);
  }
    
  fflush(stdout);

  return;
}	/* end of moduleMessage */




/*F:moduleUsage*

________________________________________________________________

		moduleUsage
________________________________________________________________

Name:		moduleUsage
Syntax:		@moduleUsage-syntax
Description:    Print usage to stdout if specified and  -usage option is used\\
                Used in function initMessage(..)
Side effects:   Exit program
Return value:   void
*/

/*<moduleUsage-syntax: */
static void moduleUsage(char *format, ...)
/*>moduleUsage-syntax: */
{
  va_list ap;
  va_start(ap, format);
  if (format){
    vsprintf(lastMessage,format, ap);
    fprintf(stdout,"%s %s\n",lastMessage,"[message options]");
    fprintf(stdout,"%s\n",
	    "message options: -usage (Print usage to screen)");
    fprintf(stdout,"%s\n",
	    "                 -noExit (No exit on errors)");
    fprintf(stdout,"%s\n",
	    "                 -m level (Message level 0: No output  ");
    fprintf(stdout,"%s\n",
	    "                                         1: Some feedback  ");
    fprintf(stdout,"%s\n",
	    "                                         2: Detailed feedback) ");

    fprintf(stdout,"%s\n",
	    "                 -w level (Warning level 0: No warnings ");
    fprintf(stdout,"%s\n",
	    "                                         1: Only serious warnings");
    fprintf(stdout,"%s\n",
	    "                                         2: All warnings)");      

    fprintf(stdout,"%s\n",
	    "                 -e level (Error level 1: Standard errors ");
    fprintf(stdout,"%s\n",
	    "                                       2: Standard errors + details)");
  }
  exit(0);
  return;
}	/* end of moduleUsage */







/*F:checkLevels*

________________________________________________________________

		checkLevels
________________________________________________________________

Name:		checkLevels
Syntax:		@checkLevels-syntax
Description:    Check that level of errors, warnings and messages are correct.
Side effects:   Print error message to stderr if the level is illegal.
Return value:   1 if errors , 0 otherwise
Global or static variables used: errorLevel, warningLevel, messageLevel
*/

/*<checkLevels-syntax: */
static int checkLevels(int errorLevel, int warningLevel, int messageLevel)
/*>checkLevels-syntax: */
{
  
  if (errorLevel != 1 && errorLevel != 2) {
    fprintf(stderr,"Illegal errorLevel\n");
    return 1;
  }
  if (warningLevel != 0 && warningLevel != 1 && warningLevel != 2) {
    fprintf(stderr,"Illegal warningLevel\n");
    return 1;
  }
  if (messageLevel != 0 && messageLevel != 1 && messageLevel != 2) {
    fprintf(stderr,"Illegal messageLevel\n");
    return 1;
  }

  return 0;
}	/* end of checkLevels */




/*F:setStdErrors*

________________________________________________________________

		setStdErrors
________________________________________________________________

Name:		setStdErrors
Syntax:		@setStdErrors-syntax
Description:    Initialize standard error messages used in function moduleError(..)
Return value: void
Global or static variables used: stdError
*/

/*<setStdErrors-syntax: */
static void setStdErrors() 
/*>setStdErrors-syntax: */
{
  int i;
  int nStd = NERRORS;

  stdError = (char **) calloc(nStd+1,sizeof(char *));
  for (i=0; i<= nStd; i++) 
    stdError[i] = (char *) calloc(80,sizeof(char));

  strcpy(stdError[NODEFAULT], "\0");
  strcpy(stdError[OPENFILE], "Opening file failed.\0");
  strcpy(stdError[READFILE], "Reading file failed.\0");
  strcpy(stdError[ALLOC], "Unable to allocate enough memory.\0");
  strcpy(stdError[MODEL], "Error in model.\0");
  strcpy(stdError[KERNEL], "Internal module error.\0");
  strcpy(stdError[WRITEFILE], "Write file failed.\0");
  strcpy(stdError[DATACHECK], "Input data inconsistency.\0");
  strcpy(stdError[CLOSEFILE], "Closing file failed.\0");

  return;
}	/* end of setStdErrors */


void moduleErrorSetNoExit(int mode)
{
	noExitOnError = mode;
	return;
}

int uiErrorSetBuffer(char *message, ...)
{
    va_list arg;

    va_start(arg, message);
    vfprintf(stderr, message, arg);
    va_end(arg);

    return(0);
}






/*F:moduleErrorLog*

________________________________________________________________

		moduleErrorLog
________________________________________________________________

Name:		moduleErrorLog
Syntax:		@moduleErrorLog-syntax
Description:    Write error messages to logfile. \\
                If errorLevel = 1: Only standard message is printed\\
                If errorLevel = 2: Standard and detailed messages are printed\\

		Allowed values for errorNumber: \\
                NODEFAULT = No default message is printed \\
                OPENFILE  = Error opening file \\
                READFILE  = Error reading from file \\
                WRITEFILE = Error writing to file \\
                ALLOC     = Unable  to allocat more space \\
                MODEL     = Error in specified  model \\
                KERNEL    = Internal module error (from kernel of program)

Side effects:   Does NOT exit program.
                Print error message to stderr if errorNumber is illegal.
Return value: void
Global or static variables used: stdError, noExitOnError, errorLevel
*/

/*<moduleErrorLog-syntax: */
void moduleErrorLog(FILE *logfile,int errorNumber, 
		    char *function, char *format, ...)
/*>moduleErrorLog-syntax: */
{

  va_list ap;

  va_start(ap, format);
  if(logfile == NULL) return;  


  if (errorLevel == 1 || errorLevel == 2) {
    fprintf(logfile,"\nERROR(%s,%s) ", progName,function);
    if (errorNumber != NODEFAULT) {
      sprintf(lastMessage,"    * ");
      sprintf(&lastMessage[6],"%s", stdError[errorNumber]);
      fprintf(logfile,"\n%s",lastMessage);
    }
  }
  if (errorLevel == 2) {
    sprintf(lastMessage,"    - ");
    vsprintf(&lastMessage[6], format, ap);
    fprintf(logfile,"\n%s\n",lastMessage);
    va_end(ap);
  }
  else
    fprintf(logfile,"\n");

/*  if (!noExitOnError)
    exit(1);        
*/
  fflush(stderr);

  return;
}	/* end of moduleErrorLog */









/*F:moduleWarningLog*

________________________________________________________________

		moduleWarningLog
________________________________________________________________

Name:		moduleWarningLog
Syntax:		@moduleWarningLog-syntax
Description:    Write warnings to logfile. \\
                If warningLevel = 0: No warnings \\
                If warningLevel = 1: Serious warnings \\
                If warningLevel = 2: All warnings \\
                \ \\
                Allowed values for warningType:\\ 
                CORRECT = Serious warning, should be corrected. \\
                CHECK   = Not serious, but should be checked.
Side effects:   Print error message to stderr if warningType illegal
Return value:   void
Global or static variables used: warningLevel
*/

/*<moduleWarningLog-syntax: */
void moduleWarningLog(FILE* logfile,int warningType, 
		      char *function, char *format, ...)
/*>moduleWarningLog-syntax: */
{

  va_list ap;

  va_start(ap, format);
  if(logfile == NULL) return;   

  if (warningType != CORRECT && warningType != CHECK)
    moduleError(NODEFAULT,"moduleWarning",
		"Warning must be of cathegory 'CORRECT' or 'CHECK");

  if (((warningLevel == 1) && (warningType == CORRECT)) ||
      ((warningLevel == 2) && (warningType == CORRECT || 
			       warningType ==CHECK))) { 
    fprintf(logfile,"\nWARNING(%s,%s) ", progName,function);
    sprintf(lastMessage,"    - ");
    vsprintf(&lastMessage[6], format, ap);
    fprintf(logfile,"\n%s\n",lastMessage);
    va_end(ap);
  }             
  
  fflush(stderr);

  return;
}	/* end of moduleWarningLog */








/*F:moduleMessageLog*

________________________________________________________________

		moduleMessageLog
________________________________________________________________

Name:		moduleMessageLog
Syntax:		@moduleMessageLog-syntax
Description:    Write MessageLogs to logfile. \\
                If messageLevel = 0: No messages \\
                If messageLevel = 1: Only runtime status \\
                If messageLevel = 2: Runtime status and detailed messages\\
                \ \\
                Allowed values for mesageType:\\ 
                STATUS    = Runtime message\\
                DETAILS   = Detailed message/information from program

Side effects:  Print error message to stderr if illegal messageType used
Return value:  void
Global or static variables used: messageLevel
*/

/*<moduleMessageLog-syntax: */
void moduleMessageLog(FILE* logfile,
		      int messageType, char *function, char *format, ...)
/*>moduleMessageLog-syntax: */
{

  va_list ap;

  va_start(ap, format);
  if(logfile == NULL) return;    

  if (messageType != STATUS && messageType != DETAILS)
    moduleError(NODEFAULT,"moduleMessage",
		"Message must be of cathegory 'STATUS' or 'DETAILS'");

  if ((messageLevel == 2 && (messageType == STATUS 
			     || messageType == DETAILS)) ||
      ((messageLevel == 1) && (messageType == STATUS))) {
    if (messageType == STATUS)
      fprintf(logfile,"\nMESSAGE(%s,%s) ", progName,function);
    sprintf(lastMessage,"    - ");
    vsprintf(&lastMessage[6], format, ap);
    fprintf(logfile,"\n%s\n",lastMessage);
    va_end(ap);
  }
    
  fflush(logfile);

  return;
}	/* end of moduleMessageLog  */






