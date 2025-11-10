#pragma once 
#include <string>

class AIClient {
    std::string endpoint;
public:
    AIClient(const std::string& apiURL);
    std::string getAIResponse(const std::string& user, const std::string& message);
};