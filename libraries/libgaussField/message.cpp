// Implementation of the class Message
#include <cstdlib>
#include "message.h"

using namespace std ;

void
Message::Warning(const char* msg, real value, ostream& stream) {
 stream << "Warning: " << msg << " is illegal.\n";
 stream << msg << " is set to " << value << endl; 

}


void 
Message::WarningKey(const char* key, const char* file_name, ostream& stream) {
  stream << "Error: Could not find keyword\" " << key << "\"\n";
  stream << "in file \"" << file_name << '"' << endl;

}

void 
Message::FatalError(const char* msg, ostream& stream) {
  stream << "Fatal error! " << msg << endl;
  exit(1);
}

void 
Message::Progress(const char* msg, ostream& stream) {
  stream << "Starting " << msg << endl;
}

void 
Message::Finish(const char* msg, ostream& stream) {
  stream << "Finished with " << msg << endl;

}
