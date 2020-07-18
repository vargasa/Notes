#include <iostream>

struct LinkedList {

  struct Element;

  Element* Current = NULL;
  Element* First = NULL;

  int operator[](const uint& a) {
    return Get(a);
  }

  struct Element{
    int Value;
    Element* Next;

    Element(): Value(0), Next(NULL) { }
    Element(const int& a) : Value(a), Next(NULL){}
  };

  Element* Push(const int& vv){
    Element *b = new Element(vv);
    if (Current != NULL) {
      (*Current).Next = b;
    } else {
      First = b;
    }
    Current = b;
    return b;
  }

  Element* Locate(const uint& position){
    Current = First;
    for(int i = 0; i < position; i++){
      Current = (*Current).Next;
    }
    return Current;
  }

  int Get(uint idx){
    Locate(idx);
    return (*Current).Value;
  }

  void Insert(const int& vv, const uint& position){
    /*Assumming position exist*/
    Current = Locate(position-1);
    Element* Old = Current;
    Element* OldNext = Old->Next;
    Element* Inserted = Push(vv);
    Old->Next = Inserted;
    Inserted->Next = OldNext;
  }

  void Delete(const uint& idx){
    /*Assumming idx actually exist*/
    Current = Locate(idx);
    Element* Old = Current;
    Element* OldNext = Old->Next;
    Element* Prev = Locate(idx == 0? 0 : idx-1);
    Prev->Next = OldNext;
    delete Old;
    Current = Locate(idx);
  }

  ~LinkedList(){}
};


int main(){

  LinkedList l;

  for(uint i = 0; i< 10 ;i++){
    l.Push((i+1)*5);
  }

  std::cout << "************\n";
  for (uint i = 0; i < 5 ; i++) {
    std::cout << l.Get(i) << std::endl;
  }

  l.Insert(12345,2);

  std::cout << "************\n";

  for (uint i = 0; i < 5 ; i++) {
    std::cout << l.Get(i) << std::endl;
  }

  l.Insert(666,3);
  l.Delete(3);

  std::cout << "************\n";

  for (uint i = 0; i < 6 ; i++) {
    std::cout << l[i] << std::endl;
  }

  return 0;
}
