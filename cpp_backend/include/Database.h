#pragma once
#include <string>

class Database{
    std::string dbpath;
public:
    Database(const std::string&path);
    void saveMessage(const std::string& user, const std::string& message);
};