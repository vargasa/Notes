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



int main(){

  rapidxml::file<> xml1("renaissance13Fq12020_holding.xml");
  rapidxml::file<> xml2("renaissance13Fq22020_holding.xml");

  rapidxml::xml_document<> doc1;
  doc1.parse<0>(xml1.data());

  rapidxml::xml_document<> doc2;
  doc2.parse<0>(xml2.data());

  rapidxml::xml_node<>* row = doc2.first_node()->first_node();

  std::map<float,std::string> delta;

  std::string cusip;

  while(row->next_sibling()) {
    cusip = row->first_node("cusip")->value();
    rapidxml::xml_node<>* matchNode = getNode(doc1.first_node(), cusip);
    if(matchNode){
      int oldShares = getNShares(matchNode);
      int newShares = getNShares(row);
      assert(oldShares != 0);
      delta.emplace((float)(newShares - oldShares)/(float)oldShares, cusip);
    }
    row = row->next_sibling();
  }

  for(const auto p: delta){
    std::cout << p.first << "\t" << p.second << "\t" << getNode(doc2.first_node(),p.second)->first_node("nameOfIssuer")->value() <<std::endl;
  }
  return 0;
}
