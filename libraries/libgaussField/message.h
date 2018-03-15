//  Declaration of the class Message

#ifndef MESSAGE_H
#define MESSAGE_H

#include "definitions.h"
#include <iostream>
class Message {

 public:
  static void Warning(const char* msg, real value = 0.0,
		      std::ostream& stream = std::cout);

  static void WarningKey(const char* key, const char* file_name,
			 std::ostream& stream = std::cout);

  static void FatalError(const char* msg, std::ostream& stream = std::cout);

  static void Progress(const char* msg, std::ostream& stream = std::cout);
  static void Finish(const char* msg, std::ostream& stream = std::cout);


};

#endif
