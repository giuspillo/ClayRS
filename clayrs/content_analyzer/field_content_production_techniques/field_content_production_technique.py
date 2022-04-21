from abc import ABC, abstractmethod
from typing import List, Union, Callable, Optional

from scipy.sparse import csr_matrix

from clayrs.content_analyzer.content_representation.content import FieldRepresentation, FeaturesBagField, \
    SimpleField
from clayrs.content_analyzer.information_processor.information_processor import InformationProcessor
from clayrs.content_analyzer.raw_information_source import RawInformationSource
from clayrs.utils.check_tokenization import check_not_tokenized


class FieldContentProductionTechnique(ABC):
    """
    Generic abstract class used to define the techniques that can be applied to the content's fields in order to
    produce their complex semantic representations.

    The FieldContentProductionTechnique creates, for each given content's raw data, the field's representation for a
    specific field
    """

    def __init__(self):
        self.__lang = "EN"

    @property
    def lang(self):
        return self.__lang

    @lang.setter
    def lang(self, lang: str):
        self.__lang = lang

    @staticmethod
    def process_data(data: str, preprocessor_list: List[InformationProcessor]) -> Union[List[str], str]:
        """
        The data passed as argument is processed using the preprocessor list (also given as argument) and is
        then returned

        Args:
            data (str): data on which each preprocessor, in the preprocessor list, will be used
            preprocessor_list (List[InformationProcessor]): list of preprocessors to apply to the data

        Returns:
            processed_data (Union[List[str], str): it could be a list of tokens created from the original data
            or the data in string form
        """
        processed_data = data
        for preprocessor in preprocessor_list:
            processed_data = preprocessor.process(processed_data)

        return processed_data

    @abstractmethod
    def produce_content(self, field_name: str, preprocessor_list: List[InformationProcessor],
                        source: RawInformationSource) -> List[FieldRepresentation]:
        """
        Abstract method that defines the methodology used by a technique to produce a list of FieldRepresentation.
        This list of FieldRepresentation objects contains all the complex representations referring to a specific
        field for each content. So if there were 3 contents (in their original/raw form) passed to the method in total,
        there would be 3 elements in the list (one for each content) and each one of these elements would be the
        representation generated by the technique. The data contained in the field for each content is also
        pre-processed by a list of information processors

        EXAMPLE

            contents to process: content1, content2, content3.
            each content contains a 'Plot' and a 'Title' field.
            if the goal is to create the representations for the field 'Plot' the method produce_content will take

            produce_content('Plot', [], raw data of the contents)

            this method will produce a list in the following form:

            [FieldRepresentation for content1, FieldRepresentation for content2, FieldRepresentation for content3]
            where each FieldRepresentation refers to the 'Plot' field of the designated content

            in this example the processor list didn't contain any information processor. If a processor list containing
            information processors was defined, the method would be:

            produce_content('Plot', [NLTK()], raw data of the contents)

            the NLTK() processor will be applied to the data contained in the field 'Plot' for each content and, after
            this process, the field representation will be elaborated.

        Args:
             field_name (str): name of the contents' field on which the technique will be applied
             preprocessor_list (List[InformationProcessor]): list of information processors that will pre-process the
                data contained in the field for each content
            source (RawInformationSource): source where the raw data of the contents is stored

        Returns:
            representation_list(List[FieldRepresentation]): list containing the representations generated by the
                technique for each content on a specific field
        """
        raise NotImplementedError


class SingleContentTechnique(FieldContentProductionTechnique):
    """
    Technique specialized in the production of representations that don't need any external information in order
    to be processed. This type of technique only considers the raw data within the content's field to create
    the complex representation
    """

    def __init__(self):
        super().__init__()

    def produce_content(self, field_name: str, preprocessor_list: List[InformationProcessor],
                        source: RawInformationSource) -> List[FieldRepresentation]:
        """
        This method creates a list of FieldRepresentation objects, where each object is associated to a content
        and a specific field from the ones in said content. In order to do so, a simple preprocessing operation
        is done on the original data of the field (for each content) followed by the creation of the complex
        representation using the processed data. The complex representations are stored in a list and returned.
        """
        representation_list: List[FieldRepresentation] = []

        # it iterates over all contents contained in the source in order to retrieve the raw data
        # the data contained in the field_name is processed using each information processor in the processor_list
        # the data is passed to the method that will create the single representation
        for content_data in source:
            processed_data = self.process_data(content_data[field_name], preprocessor_list)
            representation_list.append(self.produce_single_repr(processed_data))

        return representation_list

    @abstractmethod
    def produce_single_repr(self, field_data: Union[List[str], str]) -> FieldRepresentation:
        """
        This method creates a single FieldRepresentation using the field data only (in the complete process made by the
        produce_content method, the data also goes through pre-processing)

        Args:
             field_data (str): data contained in a specific field

        Returns:
            FieldRepresentation: complex representation created using the field data
        """
        raise NotImplementedError


class CollectionBasedTechnique(FieldContentProductionTechnique):
    """
    Technique specialized in the production of representations that are in need of the entire collection in order
    to be processed. This type of technique performs a refactoring operation on the original dataset,
    so that each content in the collection is modified accordingly to the technique's needs
    """

    def __init__(self):
        super().__init__()

    def produce_content(self, field_name: str, preprocessor_list: List[InformationProcessor],
                        source: RawInformationSource) -> List[FieldRepresentation]:
        """
        This method creates a list of FieldRepresentation objects, where each object is associated to a content
        and a specific field from the ones in said content. In order to do so, the entire dataset where the original
        contents are stored has to be modified (and also processed using the preproccesors). After that, it re-creates
        the content_id for each content and uses it to retrieve the content from the refactored dataset. Finally, the
        refactored dataset is deleted.
        """
        # the contents in the collection are modified by the technique
        # in this phase the data is also processed using the preprocessor_list
        dataset_len = self.dataset_refactor(source, field_name, preprocessor_list)

        representation_list: List[FieldRepresentation] = []

        # produces the representation, retrieving it from the dataset given the content's position in the refactored
        # dataset

        for i in range(0, dataset_len):
            representation_list.append(self.produce_single_repr(i))

        # once the operation is complete the refactored collection is deleted
        self.delete_refactored()

        return representation_list

    @abstractmethod
    def produce_single_repr(self, content_position: int) -> FieldRepresentation:
        """
        This method creates a single FieldRepresentation using the content position only. The content position is used
        to retrieve the corresponding content from the dataset modified during the content creation process.

        Args:
             content_position (int): position of the content in the dataset

        Returns:
            FieldRepresentation: complex representation created or retrieved from the refactored dataset using the
                content_position
        """
        raise NotImplementedError

    @abstractmethod
    def dataset_refactor(self, information_source: RawInformationSource, field_name: str,
                         preprocessor_list: List[InformationProcessor]) -> int:
        """
        This method restructures the raw data in a way functional to the final representation

        Args:
            information_source (RawInformationSource): source containing the raw data of the contents
            field_name (str): field interested in the content production process on which the refactor will be based on
            preprocessor_list (List[InformationProcessor]): list of preproccesors applied to the data in the field_name
                for each content during the refactoring operation

        Returns:
            length of the refactored dataset
        """
        raise NotImplementedError

    @abstractmethod
    def delete_refactored(self):
        """
        Once the content production phase is completed, the refactored dataset is useless. This method will delete the
        refactored dataset
        """
        raise NotImplementedError


class OriginalData(FieldContentProductionTechnique):
    """
    Technique used to retrieve the original data within the content's raw source without applying any
    processing operation. This technique is particularly useful if the user wants to keep the original
    data of the contents
    """

    def __init__(self, dtype: Callable = str):
        super().__init__()
        self.__dtype = dtype

    def produce_content(self, field_name: str, preprocessor_list: List[InformationProcessor],
                        source: RawInformationSource) -> List[SimpleField]:
        """
        The contents' raw data in the given field_name is extracted and stored in a SimpleField object.
        The SimpleField objects created are stored in a list which is then returned.
        No further operations are done on the data in order to keep it in the original form.
        Because of that the preprocessor_list is ignored and not used by this technique
        """

        representation_list: List[SimpleField] = []

        for content_data in source:
            processed_data = self.process_data(content_data[field_name], preprocessor_list)
            representation_list.append(SimpleField(self.__dtype(check_not_tokenized(processed_data))))

        return representation_list

# DECODE POSSIBLE REPRESENTATION: Not implemented for now
#
# class DefaultTechnique(FieldContentProductionTechnique):
#     """
#     Default technique used when no FieldContentProductionTechnique is defined in the FieldConfig.
#     """
#
#     def __init__(self):
#         super().__init__()
#
#     def produce_content(self, field_name: str, preprocessor_list: List[InformationProcessor],
#                         source: RawInformationSource) -> List[FieldRepresentation]:
#         """
#         The content's raw data is decoded using the appropriate method (in case the data is not a string).
#         Each decoded representation is added to a list which is then returned
#         """
#         representation_list: List[FieldRepresentation] = []
#
#         for content_data in source:
#             # if a preprocessor is specified, then surely we must import the field data as a string,
#             # there's no other option
#             if len(preprocessor_list) != 0:
#                 representation = SimpleField(check_not_tokenized(self.process_data(str(content_data[field_name]),
#                                                                                    preprocessor_list)))
#
#             # If a preprocessor isn't specified, well maybe it is a complex representation:
#             # let's decode what kind of complex representation it is and import it accordingly.
#             else:
#                 representation = self.__decode_field_data(str(content_data[field_name]))
#
#             representation_list.append(representation)
#
#         return representation_list
#
#     def __decode_field_data(self, field_data: str):
#         # Decode string into dict or list
#         try:
#             loaded = json.loads(field_data)
#         except json.JSONDecodeError:
#             # in case the dict is {'foo': 1} json expects {"foo": 1}
#             reformatted_field_data = field_data.replace("\'", "\"")
#             try:
#                 loaded = json.loads(reformatted_field_data)
#             except json.JSONDecodeError:
#                 # if it has issues decoding we consider the data as str
#                 loaded = reformatted_field_data
#
#         # By default the representation decoded is what json tells us
#         decoded = SimpleField(loaded)
#
#         # if the decoded is a list, maybe it is an EmbeddingField repr
#         if isinstance(loaded, list):
#             arr = np.array(loaded)
#
#             # if the array values has can be converted into floats then we consider it as a dense vector
#             # else it is not and we do nothing
#             try:
#                 arr = arr.astype(float)
#                 decoded = EmbeddingField(arr)
#
#             # Can't be converted
#             except ValueError:
#                 pass
#
#         # if the decoded is a dict, maybe it is a FeaturesBagField
#         elif isinstance(loaded, dict):
#             # if all values of the dict are numbers or can be converted into numbers,
#             # then we consider it as a bag of words
#             # else it is not and we do nothing
#             if len(loaded.values()) != 0:
#                 try:
#                     dict_converted = {k: float(loaded[k]) for k in loaded}
#
#                     decoded = FeaturesBagField(dict_converted)
#
#                 # Can't be converted
#                 except ValueError:
#                     pass
#
#         return decoded


class TfIdfTechnique(CollectionBasedTechnique):
    """
    Abstract class that generalizes the implementations that produce a Bag of words with tf-idf metric
    """

    def __init__(self):
        super().__init__()
        self._tfidf_matrix: Optional[csr_matrix] = None
        self._feature_names: Optional[List[str]] = None

    def produce_single_repr(self, content_position: int) -> FeaturesBagField:
        """
        Retrieves the tf-idf values, for terms in document in the defined content_position,
        from the pre-computed word - document matrix.
        """
        nonzero_feature_index = self._tfidf_matrix[content_position, :].nonzero()[1]

        tfidf_sparse = self._tfidf_matrix.getrow(content_position).toarray()
        pos_word_tuple = [(pos, self._feature_names[pos]) for pos in nonzero_feature_index]

        return FeaturesBagField(tfidf_sparse, pos_word_tuple)

    @abstractmethod
    def dataset_refactor(self, information_source: RawInformationSource, field_name: str,
                         preprocessor_list: List[InformationProcessor]):
        raise NotImplementedError

    def delete_refactored(self):
        del self._tfidf_matrix
        del self._feature_names


class SynsetDocumentFrequency(CollectionBasedTechnique):
    """
    Abstract class that generalizes implementations that use synsets
    """
    def __init__(self):
        super().__init__()
        self._synset_matrix: Optional[csr_matrix] = None
        self._synset_names: Optional[List[str]] = None

    def produce_single_repr(self, content_position: int) -> FeaturesBagField:
        """
        Retrieves the tf-idf values, for terms in document in the defined content_position,
        from the pre-computed word - document matrix.
        """
        nonzero_feature_index = self._synset_matrix[content_position, :].nonzero()[1]

        count_dense = self._synset_matrix.getrow(content_position).toarray()
        pos_word_tuple = [(pos, self._synset_names[pos]) for pos in nonzero_feature_index]

        return FeaturesBagField(count_dense, pos_word_tuple)

    @abstractmethod
    def dataset_refactor(self, information_source: RawInformationSource, field_name: str,
                         preprocessor_list: List[InformationProcessor]):
        raise NotImplementedError

    def delete_refactored(self):
        del self._synset_matrix
        del self._synset_names
