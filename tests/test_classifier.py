from unittest.mock import patch

import pytest

from autokeras.classifier import *
from autokeras import constant
from autokeras.generator import RandomConvClassifierGenerator
from tests.common import clean_dir


def test_train_x_array_exception():
    clf = ImageClassifier()
    with pytest.raises(Exception) as info:
        clf.fit(15, [])
    assert str(info.value) == 'x_train should at least has 2 dimensions.'


def test_xy_dim_exception():
    clf = ImageClassifier()
    with pytest.raises(Exception) as info:
        clf.fit([[1, 2], [3, 4]], [6, 7, 8])
    assert str(info.value) == 'x_train and y_train should have the same number of instances.'


def test_x_float_exception():
    clf = ImageClassifier()
    with pytest.raises(Exception) as info:
        clf.fit([[1, 'abc'], [3, 4]], [7, 8])
    assert str(info.value) == 'x_train should only contain numerical data.'


def simple_transform(_):
    generator = RandomConvClassifierGenerator(input_shape=(2, 1), n_classes=2)
    return [generator.generate(), generator.generate()]


@patch('autokeras.search.transform', side_effect=simple_transform)
@patch('autokeras.search.ModelTrainer.train_model', side_effect=lambda: None)
def test_fit_predict(_, _1):
    constant.MAX_ITER_NUM = 2
    constant.MAX_MODEL_NUM = 2
    constant.EPOCHS_EACH = 1
    path = 'tests/resources/temp'
    clf = ImageClassifier(path=path, verbose=False)
    train_x = np.array([[[1], [2]], [[3], [4]]])
    train_y = np.array(['a', 'b'])
    clf.fit(train_x, train_y)
    results = clf.predict(train_x)
    assert all(map(lambda result: result in np.array(['a', 'b']), results))
    clean_dir(path)


def simple_transform2(_):
    generator = RandomConvClassifierGenerator(input_shape=(25, 1), n_classes=5)
    return [generator.generate(), generator.generate()]


@patch('autokeras.search.transform', side_effect=simple_transform2)
@patch('autokeras.search.ModelTrainer.train_model', side_effect=lambda: None)
def test_fit_predict2(_, _1):
    path = 'tests/resources/temp'
    clf = ImageClassifier(path=path, verbose=False)
    constant.MAX_ITER_NUM = 1
    constant.MAX_MODEL_NUM = 1
    constant.EPOCHS_EACH = 1
    train_x = np.random.rand(100, 25, 1)
    test_x = np.random.rand(100, 25, 1)
    train_y = np.random.randint(0, 5, 100)
    clf.fit(train_x, train_y)
    results = clf.predict(test_x)
    assert len(results) == 100
    clean_dir(path)


@patch('autokeras.search.transform', side_effect=simple_transform2)
@patch('autokeras.search.ModelTrainer.train_model', side_effect=lambda: None)
def test_save_continue(_, _1):
    constant.MAX_ITER_NUM = 1
    constant.MAX_MODEL_NUM = 1
    constant.EPOCHS_EACH = 1
    train_x = np.random.rand(100, 25, 1)
    test_x = np.random.rand(100, 25, 1)
    train_y = np.random.randint(0, 5, 100)
    path = 'tests/resources/temp'
    clf = ImageClassifier(path=path, verbose=False)
    clf.n_epochs = 100
    clf.fit(train_x, train_y)
    assert len(clf.searcher.history) == 1

    constant.MAX_MODEL_NUM = 2
    clf = ImageClassifier(verbose=False, path=path)
    clf.fit(train_x, train_y)
    results = clf.predict(test_x)
    assert len(results) == 100
    assert len(clf.searcher.history) == 2
    clean_dir(path)
