#include "Server.h"
#include "AIClient.h"
#include "Database.h"
#include <httplib.h>
#include <nlohmann/json.hpp>
#include <iostream>

using json = nlohmann::json;
using namespace httplib;
using namespace std;

void BackendServer::start(int port){
    httplib::Server svr;  
    Database db("data/users.db");
    AIClient aiCLient("http://127.0.0.1:8000/respond");

    svr.Post("/message", [&](const Request& req, Response& res){
        try{
            auto bodyJson = json::parse(req.body);
            std::string user = bodyJson["user"];
            std::string message = bodyJson["message"];
            std::cout << "[INCOMING] " << user << ": " << message << std::endl;
            db.saveMessage(user,message);
            std::string aiResponse = aiCLient.getAIResponse(user,message);
            json reply = {{"reply",aiResponse}};
            res.set_content(reply.dump(), "application/json");
            
        } catch (std::exception& e){
            res.status = 400;
            res.set_content(std::string("Error: ") + e.what(), "text/plain");
        }
    });
    std::cout << " TTB backend running on port " << port << std::endl;
    svr.listen("0.0.0.0", port);
}