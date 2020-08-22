/*
  wget -c https://www.sec.gov/Archives/edgar/data/1037389/000103738920000321/renaissance13Fq22020_holding.xml
  wget -c https://www.sec.gov/Archives/edgar/data/1037389/000103738920000320/renaissance13Fq12020_holding.xml

  ./a.out renaissance13Fq12020_holding.xml renaissance13Fq22020_holding.xml

*/

#include <iostream>
#include <fstream>
#include <array>
#include <string>
#include <cstring>
#include <map>
#include <functional>
#include <bits/stdc++.h>
#include "rapidXML/rapidxml.hpp"
#include "rapidXML/rapidxml_utils.hpp"

rapidxml::xml_node<>* getNode(const rapidxml::xml_node<>* root,
                              const std::string& cusip){

  rapidxml::xml_node<>* nn =  root->first_node();

  do {
    if (nn->first_node("cusip")->value() == cusip) return nn;
    nn = nn->next_sibling();
  } while(nn->next_sibling());

  return 0;
}


bool sortByValue(const std::tuple<std::string, int, float>& a,
                 const std::tuple<std::string, int, float>& b){
  return !(std::get<1>(a) < std::get<1>(b));
}


////////////////// Position ///////////////////
class Position {

  std::string nameOfIssuer;
  std::string cusip;
  int value;
  int nShares;
  rapidxml::xml_node<>* next;
  bool valid;

  std::string getAsString( const rapidxml::xml_node<>* node, const std::string& tag);
  int getAsInt( const rapidxml::xml_node<>* node, const std::string& tag);

public:
  Position(const rapidxml::xml_node<>* nn);
  ~Position() = default;
  std::string getCusip() { return cusip; }
  std::string getIssuer() { return nameOfIssuer; }
  int getValue() { return value; }
  int getnShares() { return nShares; }
  rapidxml::xml_node<>* getNext() { return next; }
  bool isValid() { return valid; }
};

Position::Position(const rapidxml::xml_node<>* nn) :
  nameOfIssuer(nn? getAsString(nn,"nameOfIssuer") : ""),
  cusip(nn? getAsString(nn,"cusip") : ""),
  value(nn? getAsInt(nn,"value"):0),
  nShares(nn? getAsInt(nn->first_node("shrsOrPrnAmt"),"sshPrnamt"):0),
  next(nn? nn->next_sibling(): 0),
  valid(nn)
{};

std::string Position::getAsString(const rapidxml::xml_node<>* node, const std::string& tag){
  rapidxml::xml_node<>* nn = node->first_node(tag.c_str());
  assert(nn);
  size_t s = nn->value_size();
  char ss[s+1];
  memcpy(ss,nn->value(),s+1);
  return std::string(ss);
}

int Position::getAsInt(const rapidxml::xml_node<>* node, const std::string& tag){
  rapidxml::xml_node<>* nn = node->first_node(tag.c_str());
  assert(nn);
  size_t s = nn->value_size();
  char ss[s];
  memcpy(ss,nn->value(),s);
  int x;
  sscanf(ss, "%d", &x);
  return x;
}
////////////////// Position ///////////////////

int main(int argc, char *argv[]){

  assert(argc == 3);

  rapidxml::file<> xml1(argv[1]);
  rapidxml::file<> xml2(argv[2]);

  rapidxml::xml_document<> doc1;
  doc1.parse<0>(xml1.data());

  rapidxml::xml_document<> doc2;
  doc2.parse<0>(xml2.data());

  auto pos2 = Position(doc2.first_node()->first_node());

  std::vector<std::tuple<std::string,int,float>> delta;
  std::vector<std::tuple<std::string,int,float>> newAdd;

  std::string cusip;
  int totalPos2 = 0;
  do {
    cusip = pos2.getCusip();
    totalPos2 += pos2.getValue();
    auto pos1 = Position(getNode(doc1.first_node(), cusip));
    if(pos1.isValid()){
      int oldShares = pos1.getnShares();
      int newShares = pos2.getnShares();
      assert(oldShares != 0);
      float ratio = (float)(newShares - oldShares)/(float)oldShares;
      delta.emplace_back(std::make_tuple(cusip,pos2.getValue(),ratio));
    } else {
      newAdd.emplace_back(std::make_tuple(cusip,pos2.getValue(),1.));
    }
    pos2 = Position(pos2.getNext());
  } while (pos2.getNext());

  std::sort(delta.begin(),delta.end(),sortByValue);

  std::string c1 = "bgcolor=\"lightpink\"";
  std::string c2 = "bgcolor=\"lightgreen\"";
  std::string *c;

  std::cout << "<table>\n" ;
  int ii = 0;
  for(const auto& tp: delta){
    c = std::get<2>(tp) < 0? &c1:&c2;
    Position p = Position(getNode(doc2.first_node(),std::get<0>(tp)));
    std::cout << "\t<tr " << *c << "><td>" << ++ii << "</td><td>"
              << static_cast<float>(std::get<1>(tp))*100.f/static_cast<float>(totalPos2) << "</td><td>"
              << p.getIssuer() << "</td><td>" << p.getCusip() << "</td><td>"
              << std::get<2>(tp)*100 << "%</td></tr>" <<std::endl;
  }
  std::cout << "</table>\n";


  std::sort(newAdd.begin(),newAdd.end(),sortByValue);
  std::cout << "<table>\n" ;

  for(const auto& tp: newAdd){
    Position p = Position(getNode(doc2.first_node(),std::get<0>(tp)));
    std::cout << "\t<tr " << c1 << "><td>" << std::get<0>(tp) << ++ii << "</td><td>" << std::get<1>(tp)
              << "</td><td>" << p.getIssuer() << "</td>" << "\n" ;
  }
  std::cout << "</table>\n";
  return 0;
}
