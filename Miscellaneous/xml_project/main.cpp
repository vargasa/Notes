/*
  wget -c https://www.sec.gov/Archives/edgar/data/1037389/000103738920000321/renaissance13Fq22020_holding.xml
  wget -c https://www.sec.gov/Archives/edgar/data/1037389/000103738920000320/renaissance13Fq12020_holding.xml
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

  while(nn->next_sibling()){
    nn = nn->next_sibling();
    if (nn->first_node("cusip")->value() == cusip) return nn;
  }

  return 0;
}

int getNShares(rapidxml::xml_node<>* node){
  rapidxml::xml_node<>* nn = node->first_node("shrsOrPrnAmt")->first_node("sshPrnamt");
  assert(nn);
  size_t s = nn->value_size();
  char ss[s];
  memcpy(ss,nn->value(),s);
  return atoi(ss);
}

int getValue(rapidxml::xml_node<>* node){
  rapidxml::xml_node<>* nn = node->first_node("value");
  assert(nn);
  size_t s = nn->value_size();
  char ss[s];
  memcpy(ss,nn->value(),s);
  int x;
  sscanf(ss, "%d", &x);
  return x;
}

std::string getNameIssuer(rapidxml::xml_node<>* node){
  rapidxml::xml_node<>* nn = node->first_node("nameOfIssuer");
  assert(nn);
  size_t s = nn->value_size();
  char ss[s];
  memcpy(ss,nn->value(),s);
  return std::string(ss);
}

bool sortByValue(const std::tuple<std::string, int, float>& a,
                 const std::tuple<std::string, int, float>& b){
  return !(std::get<1>(a) < std::get<1>(b));
}

int main(){

  rapidxml::file<> xml1("renaissance13Fq12020_holding.xml");
  rapidxml::file<> xml2("renaissance13Fq22020_holding.xml");

  rapidxml::xml_document<> doc1;
  doc1.parse<0>(xml1.data());

  rapidxml::xml_document<> doc2;
  doc2.parse<0>(xml2.data());

  rapidxml::xml_node<>* row = doc2.first_node()->first_node();

  std::vector<std::tuple<std::string,int,float>> delta;

  std::string cusip;

  while(row->next_sibling()) {
    cusip = row->first_node("cusip")->value();
    rapidxml::xml_node<>* matchNode = getNode(doc1.first_node(), cusip);
    if(matchNode){
      int oldShares = getNShares(matchNode);
      int newShares = getNShares(row);
      assert(oldShares != 0);
      float d = (float)(newShares - oldShares)/(float)oldShares;
      delta.emplace_back(std::make_tuple(cusip,getValue(matchNode),d));
    }
    row = row->next_sibling();
  }

  std::sort(delta.begin(),delta.end(),sortByValue);

  std::string c1 = "bgcolor=\"lightpink\"";
  std::string c2 = "bgcolor=\"lightgreen\"";
  std::string *c;

  std::cout << "<table>\n" ;
  int ii = 0;
  for(const auto& tp: delta){
    c = std::get<2>(tp) < 0? &c1:&c2;
    rapidxml::xml_node<>* nn = getNode(doc2.first_node(),std::get<0>(tp));
    std::cout << "\t<tr " << *c << "><td>" << ++ii << "</td><td>"
              << std::get<1>(tp) << "</td><td>"
              << getNameIssuer(nn) << "</td><td>"
              << std::get<2>(tp)*100 << "%</td></tr>" <<std::endl;
  }
  std::cout << "</table>\n";
  return 0;
}
